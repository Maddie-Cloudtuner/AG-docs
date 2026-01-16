#!/usr/bin/env python3
import sys
import gi
import time
import argparse

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        sys.stdout.write("End-of-stream\n")
        loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        loop.quit()
    elif t == Gst.MessageType.STATE_CHANGED:
        old_state, new_state, pending_state = message.parse_state_changed()
        if message.src.get_name() == "pipeline0":
            print(f"Pipeline State: {Gst.Element.state_get_name(old_state)} -> {Gst.Element.state_get_name(new_state)}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Debug RTSP Stream using GStreamer uridecodebin")
    parser.add_argument("--uri", help="RTSP URI to test", required=True)
    parser.add_argument("--proto", help="RTSP Protocol (tcp/udp)", default="tcp")
    args = parser.parse_args()

    Gst.init(None)

    print(f"Testing URI: {args.uri}")

    pipeline = Gst.Pipeline()
    
    # Create uridecodebin
    source = Gst.ElementFactory.make("uridecodebin", "source")
    source.set_property("uri", args.uri)
    
    # Force connection speed (mostly for TCP)
    # The 'protocols' property is not always available on uridecodebin directly, 
    # usually it propagates to rtspsrc. We rely on smart defaults or manual rtspsrc testing 
    # if this high-level check fails. 
    # But for uridecodebin, we can try to hook "source-setup" signal to configure rtspsrc.
    
    def source_setup(uridecodebin, source_element):
        print(f"Source Setup: {source_element.get_name()}")
        if "rtspsrc" in source_element.get_name():
            print(f"Configuring rtspsrc: protocols={args.proto}")
            if args.proto == "tcp":
                source_element.set_property("protocols", Gst.RTSPProfile.TCP)
            else:
                 source_element.set_property("protocols", Gst.RTSPProfile.UDP)

    source.connect("source-setup", source_setup)

    sink = Gst.ElementFactory.make("fakesink", "sink")
    
    pipeline.add(source)
    pipeline.add(sink)

    # Link pads dyanmically
    def on_pad_added(src, pad):
        print(f"Pad added: {pad.get_name()}")
        sink_pad = sink.get_static_pad("sink")
        if not sink_pad.is_linked():
            pad.link(sink_pad)
            print("Linked to sink.")

    source.connect("pad-added", on_pad_added)

    # Loop
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    print("Starting pipeline...")
    pipeline.set_state(Gst.State.PLAYING)

    try:
        # Run for 10 seconds effectively, or until error
        GLib.timeout_add_seconds(10, loop.quit)
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.set_state(Gst.State.NULL)
        print("Pipeline stopped.")

if __name__ == "__main__":
    main()