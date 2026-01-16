#!/usr/bin/env python3
import sys
import time
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# --- YOUR 4 CAMERAS ---
RTSP_URLS = [
    "rtsp://admin:hik%402024@192.168.0.64:554/Streaming/Channels/101",
    "rtsp://admin:hik%402024@192.168.0.65:554/Streaming/Channels/101",
    "rtsp://admin:hik%402024@192.168.0.66:554/Streaming/Channels/101",
    "rtsp://admin:hik%402024@192.168.0.67:554/Streaming/Channels/101"
]

# Config Paths
CONFIG_PRIMARY = "configs/deepstream/config_primary_gie.txt"
CONFIG_FIRE    = "configs/deepstream/config_fire_gie.txt"
CONFIG_FIGHT   = "configs/deepstream/config_fight_gie.txt"

def osd_sink_pad_buffer_probe(pad, info, u_data):
    """
    Prints detections to console. 
    """
    gst_buffer = info.get_buffer()
    if not gst_buffer: return Gst.PadProbeReturn.OK

    try:
        import pyds
    except ImportError:
        return Gst.PadProbeReturn.OK

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list
    
    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        # Check for objects in this frame
        l_obj = frame_meta.obj_meta_list
        
        if l_obj is not None:
            # Only print if something is detected to keep console clean
            print(f"--- Cam {frame_meta.source_id} Frame {frame_meta.frame_num} ---")
            
            while l_obj is not None:
                try:
                    obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
                except StopIteration:
                    break
                
                # Identify Model
                model_name = "UNKNOWN"
                if obj_meta.unique_component_id == 1: model_name = "PERSON"
                elif obj_meta.unique_component_id == 2: model_name = "FIRE"
                elif obj_meta.unique_component_id == 3: model_name = "FIGHT"
                
                print(f"  [{model_name}] {obj_meta.obj_label} ({obj_meta.confidence:.2f})")

                try: 
                    l_obj = l_obj.next
                except StopIteration:
                    break
        
        try:
            l_frame = l_frame.next
        except StopIteration:
            break
            
    return Gst.PadProbeReturn.OK

def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        sys.stdout.write("End of stream\n")
        loop.quit()
    elif t == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        sys.stderr.write("Warning: %s: %s\n" % (err, debug))
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        loop.quit()
    elif t == Gst.MessageType.STATE_CHANGED:
        old_state, new_state, pending_state = message.parse_state_changed()
        if new_state == Gst.State.PLAYING:
            print(f"Pipeline running! (State: PLAYING)")
    return True

def main():
    Gst.init(None)
    print(f"Initializing Pipeline with {len(RTSP_URLS)} streams...")

    pipeline = Gst.Pipeline()

    # 1. Stream Muxer
    streammux = Gst.ElementFactory.make("nvstreammux", "stream-muxer")
    streammux.set_property('width', 640)
    streammux.set_property('height', 384)
    streammux.set_property('batch-size', len(RTSP_URLS)) # 4
    streammux.set_property('batched-push-timeout', 40000)
    streammux.set_property('live-source', 1) # CRITICAL FIX
    pipeline.add(streammux)

    # 2. Add Sources
    for i, url in enumerate(RTSP_URLS):
        print(f"Adding Stream {i}: {url}")
        source = Gst.ElementFactory.make("uridecodebin", f"source_{i}")
        source.set_property("uri", url)
        
        # Standard decodebin -> queue -> conv -> caps -> mux logic
        queue = Gst.ElementFactory.make("queue", f"q_pre_mux_{i}")
        conv = Gst.ElementFactory.make("nvvideoconvert", f"conv_{i}")
        caps = Gst.ElementFactory.make("capsfilter", f"caps_{i}")
        caps.set_property("caps", Gst.Caps.from_string("video/x-raw(memory:NVMM)"))

        pipeline.add(source)
        pipeline.add(queue)
        pipeline.add(conv)
        pipeline.add(caps)

        # Linking
        queue.link(conv)
        conv.link(caps)

        # Dynamic Pad Linking for uridecodebin
        def on_pad_added(src, pad, q=queue):
            sink_pad = q.get_static_pad("sink")
            if not sink_pad.is_linked():
                pad.link(sink_pad)
        source.connect("pad-added", on_pad_added)

        # Link to Muxer
        sink_pad = streammux.request_pad_simple(f"sink_{i}")
        caps.get_static_pad("src").link(sink_pad)

    # 3. Models (Inference)
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    pgie.set_property('config-file-path', CONFIG_PRIMARY)
    pgie.set_property("batch-size", len(RTSP_URLS))

    fire_gie = Gst.ElementFactory.make("nvinfer", "fire-inference")
    fire_gie.set_property("config-file-path", CONFIG_FIRE)
    fire_gie.set_property("batch-size", len(RTSP_URLS))

    fight_gie = Gst.ElementFactory.make("nvinfer", "fight-inference")
    fight_gie.set_property("config-file-path", CONFIG_FIGHT)
    fight_gie.set_property("batch-size", len(RTSP_URLS))

    # 4. Queues (Deadlock Prevention)
    q_pgie = Gst.ElementFactory.make("queue", "q_pgie")
    q_fire = Gst.ElementFactory.make("queue", "q_fire")
    q_fight = Gst.ElementFactory.make("queue", "q_fight")

    # 5. Output
    sink = Gst.ElementFactory.make("fakesink", "fake-renderer")
    sink.set_property("sync", 0) # CRITICAL FIX
    sink.set_property("async", 0) # CRITICAL FIX

    # Add Elements
    pipeline.add(pgie)
    pipeline.add(q_pgie)
    pipeline.add(fire_gie)
    pipeline.add(q_fire)
    pipeline.add(fight_gie)
    pipeline.add(q_fight)
    pipeline.add(sink)

    # Link Chain: Mux -> PGIE -> Q -> Fire -> Q -> Fight -> Q -> Sink
    streammux.link(pgie)
    pgie.link(q_pgie)
    q_pgie.link(fire_gie)
    fire_gie.link(q_fire)
    q_fire.link(fight_gie)
    fight_gie.link(q_fight)
    q_fight.link(sink)

    # Attach Probe to confirm detections
    q_fight_src = q_fight.get_static_pad("src")
    q_fight_src.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)

    # Run
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    print("Starting 4-Stream Multi-Model PoC...")
    pipeline.set_state(Gst.State.PLAYING)
    
    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    pipeline.set_state(Gst.State.NULL)

if __name__ == '__main__':
    sys.exit(main())