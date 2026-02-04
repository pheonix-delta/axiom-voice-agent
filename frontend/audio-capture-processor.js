// Audio Worklet Processor for capturing microphone input
// Sends 512-sample chunks to main thread for VAD processing

class AudioCaptureProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.bufferSize = 512; // Silero VAD requirement
        this.buffer = new Float32Array(this.bufferSize);
        this.bufferIndex = 0;
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];

        if (input.length > 0) {
            const inputChannel = input[0]; // Mono channel

            for (let i = 0; i < inputChannel.length; i++) {
                this.buffer[this.bufferIndex++] = inputChannel[i];

                // When buffer is full, send to main thread
                if (this.bufferIndex >= this.bufferSize) {
                    // Send copy of buffer
                    this.port.postMessage({
                        type: 'audio',
                        data: this.buffer.slice()
                    });

                    this.bufferIndex = 0;
                }
            }
        }

        return true; // Keep processor alive
    }
}

registerProcessor('audio-capture-processor', AudioCaptureProcessor);
