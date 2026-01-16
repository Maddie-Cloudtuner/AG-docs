// ===================================
// Simple Chart Library (Lightweight)
// ===================================

class SimpleChart {
    constructor(canvasId, config) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.config = config;
        this.padding = { top: 20, right: 20, bottom: 40, left: 50 };

        // Set canvas size
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;

        this.render();
    }

    render() {
        const { labels, datasets } = this.config.data;
        const width = this.canvas.width;
        const height = this.canvas.height;
        const chartWidth = width - this.padding.left - this.padding.right;
        const chartHeight = height - this.padding.top - this.padding.bottom;

        // Clear canvas
        this.ctx.clearRect(0, 0, width, height);

        // Find max value
        const allValues = datasets.flatMap(d => d.data);
        const maxValue = Math.max(...allValues);
        const minValue = 0;
        const valueRange = maxValue - minValue;

        // Draw grid lines
        this.ctx.strokeStyle = '#E5E7EB';
        this.ctx.lineWidth = 1;
        const gridLines = 5;

        for (let i = 0; i <= gridLines; i++) {
            const y = this.padding.top + (chartHeight / gridLines) * i;
            this.ctx.beginPath();
            this.ctx.moveTo(this.padding.left, y);
            this.ctx.lineTo(width - this.padding.right, y);
            this.ctx.stroke();

            // Y-axis labels
            const value = Math.round(maxValue - (valueRange / gridLines) * i);
            this.ctx.fillStyle = '#6B7280';
            this.ctx.font = '12px Inter, sans-serif';
            this.ctx.textAlign = 'right';
            this.ctx.fillText(value, this.padding.left - 10, y + 4);
        }

        // Draw X-axis labels
        const xStep = chartWidth / (labels.length - 1);
        labels.forEach((label, index) => {
            const x = this.padding.left + xStep * index;
            const y = height - this.padding.bottom + 20;

            this.ctx.fillStyle = '#6B7280';
            this.ctx.font = '12px Inter, sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(label, x, y);
        });

        // Draw datasets
        datasets.forEach(dataset => {
            const { data, borderColor, backgroundColor, tension, borderDash, fill } = dataset;

            this.ctx.strokeStyle = borderColor;
            this.ctx.lineWidth = 3;
            this.ctx.lineCap = 'round';
            this.ctx.lineJoin = 'round';

            if (borderDash) {
                this.ctx.setLineDash(borderDash);
            } else {
                this.ctx.setLineDash([]);
            }

            // Create path
            this.ctx.beginPath();

            data.forEach((value, index) => {
                const x = this.padding.left + xStep * index;
                const y = this.padding.top + chartHeight - ((value - minValue) / valueRange) * chartHeight;

                if (index === 0) {
                    this.ctx.moveTo(x, y);
                } else {
                    if (tension > 0) {
                        // Simple curve approximation
                        const prevX = this.padding.left + xStep * (index - 1);
                        const prevY = this.padding.top + chartHeight - ((data[index - 1] - minValue) / valueRange) * chartHeight;
                        const cpX = (prevX + x) / 2;
                        this.ctx.quadraticCurveTo(cpX, prevY, x, y);
                    } else {
                        this.ctx.lineTo(x, y);
                    }
                }
            });

            this.ctx.stroke();

            // Fill area
            if (fill && backgroundColor) {
                this.ctx.lineTo(this.padding.left + xStep * (data.length - 1), height - this.padding.bottom);
                this.ctx.lineTo(this.padding.left, height - this.padding.bottom);
                this.ctx.closePath();
                this.ctx.fillStyle = backgroundColor;
                this.ctx.fill();
            }

            // Draw points
            if (!borderDash) {
                data.forEach((value, index) => {
                    const x = this.padding.left + xStep * index;
                    const y = this.padding.top + chartHeight - ((value - minValue) / valueRange) * chartHeight;

                    this.ctx.beginPath();
                    this.ctx.arc(x, y, 4, 0, Math.PI * 2);
                    this.ctx.fillStyle = borderColor;
                    this.ctx.fill();
                    this.ctx.strokeStyle = '#FFFFFF';
                    this.ctx.lineWidth = 2;
                    this.ctx.stroke();
                });
            }
        });

        this.ctx.setLineDash([]);
    }
}
