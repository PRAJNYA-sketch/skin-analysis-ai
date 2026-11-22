
const API_URL = "http://127.0.0.1:8000";

// Camera elements
const camera = document.getElementById("camera");
const canvas = document.getElementById("canvas");

const startButton = document.getElementById("start-camera");
const captureButton = document.getElementById("capture");
const stopButton = document.getElementById("stop-camera");

const cameraMessage = document.getElementById("camera-message");
const scanStatus = document.getElementById("scan-status");

let cameraStream = null;


// 1. Open camera
startButton.addEventListener("click", async () => {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: true
        });

        camera.srcObject = cameraStream;
        camera.style.display = "block";
        cameraMessage.style.display = "none";

        startButton.disabled = true;
        captureButton.disabled = false;
        stopButton.disabled = false;

        scanStatus.textContent = "Camera is ready!";

    } catch (error) {
        scanStatus.textContent = "Unable to access camera. Please allow permission.";
        console.error(error);
    }
});


// 2. Capture image and send to FastAPI
captureButton.addEventListener("click", async () => {

    if (!camera.videoWidth || !camera.videoHeight) {
        scanStatus.textContent = "Camera is not ready yet.";
        return;
    }

    canvas.width = camera.videoWidth;
    canvas.height = camera.videoHeight;

    const context = canvas.getContext("2d");
    context.drawImage(camera, 0, 0);

    canvas.toBlob(async (blob) => {

        if (!blob) {
            scanStatus.textContent = "Unable to capture image.";
            return;
        }

        const formData = new FormData();
        formData.append("file", blob, "face.jpg");

        scanStatus.textContent = "Sending image to AI server...";
        captureButton.disabled = true;

        try {
            const response = await fetch(`${API_URL}/scan-face`, {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Image upload failed");
            }

            scanStatus.textContent = result.message;

        } catch (error) {
            scanStatus.textContent = error.message;
            console.error(error);
        } finally {
            captureButton.disabled = false;
        }

    }, "image/jpeg", 0.9);
});


// 3. Stop camera
stopButton.addEventListener("click", () => {

    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }

    camera.srcObject = null;
    camera.style.display = "none";
    cameraMessage.style.display = "block";

    startButton.disabled = false;
    captureButton.disabled = true;
    stopButton.disabled = true;

    scanStatus.textContent = "Camera stopped.";
});


// 4. Upload PDF
const pdfInput = document.getElementById("pdf-file");
const uploadButton = document.getElementById("upload-pdf");
const pdfStatus = document.getElementById("pdf-status");

uploadButton.addEventListener("click", async () => {

    const file = pdfInput.files[0];

    if (!file) {
        pdfStatus.textContent = "Please select a PDF first.";
        return;
    }

    if (file.type !== "application/pdf") {
        pdfStatus.textContent = "Only PDF files are allowed.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    pdfStatus.textContent = "Uploading PDF...";
    uploadButton.disabled = true;

    try {
        const response = await fetch(`${API_URL}/upload-pdf`, {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "PDF upload failed");
        }

        pdfStatus.textContent = result.message;

    } catch (error) {
        pdfStatus.textContent = error.message;
        console.error(error);
    } finally {
        uploadButton.disabled = false;
    }
});
