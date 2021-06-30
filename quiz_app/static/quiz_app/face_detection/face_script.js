//  Script file for the face detection

let video = document.getElementById("video");

// LOAD ALL MODELS ASYNCHRONOUSLY
// tinyFaceDetector - make it fast
Promise.all([
	faceapi.nets.tinyFaceDetector.loadFromUri('/static/quiz_app/face_detection/models')
]).then(function() {
	setInterval(checkVideo,1000);
	startVideo();
})
let cameraAvailability = false;


// start the web camera
function startVideo(){
	navigator.mediaDevices.getUserMedia({ video: {}})
		.then((stream) => {
				// console the result
				console.log("Camera Found");

				cameraAvailability = true;

				// use the stream
				video.srcObject = stream;
		})
		.catch((err) => {
			// handle the error
				console.error(err.name + ": " + err.message);

				cameraAvailability = false;

				Swal.fire({
					icon: 'error',
					title: `Can't access the camera`,
					html: `Error: ${err.message}<br>Please fix the problem and refresh the page.`,
					position: 'center',
					showConfirmButton: false,
					allowOutsideClick: false,
					allowEscapeKey: false,
				});
		})
}


function checkVideo(){
	navigator.mediaDevices.getUserMedia({ video: {}})
		.then((stream) => {
				if((Swal.isVisible() && Swal.getTitle().textContent == "Can't access the camera")) {
					// console the result
					console.log("Camera Found");

					cameraAvailability = true;

					// use the stream
					video.srcObject = stream;

					Swal.close();
				}
		})
		.catch((err) => {
				console.error(err.name + ": " + err.message);

				cameraAvailability = false;

				if(!(Swal.isVisible() && Swal.getTitle().textContent == "Can't access the camera")) {
					Swal.fire({
						icon: 'error',
						title: `Can't access the camera`,
						html: `Error: ${err.message}<br>Please fix the problem and refresh the page.`,
						position: 'center',
						showConfirmButton: false,
						allowOutsideClick: false,
						allowEscapeKey: false,
					});
				}
		})
}
var personAbsence = 0;


function noPersonFound() {
	console.log(increase_suspicious_url);
	personAbsence++;
	if(personAbsence >= 10) {
		personAbsence = 0;
		$.ajax({
			type: "POST",
			url: increase_suspicious_url,
			data: {
				quiz: quiz_id,
				csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
			},
			success:function(success) {
				if(success.max_reached) {
					max_suspicion_reached();
				}
			}
		});
		Swal.fire({
			icon: 'warning',
			html: 'Please do not move away from the camera or else your test may be terminated.',
			position: 'top-right',
			toast: true,
			showConfirmButton: false,
			timer: 3000,
			timerProgressBar: true
		});
	}
}


// when the video starts playing create a canvas of same dimenstions as of video at a specific time interval
// the canvas should exactly be above the video
// creates a blue rectangle around the face of the user which means that the camera detected a face

// get the no of people detected by the camera by the detections.length
video.addEventListener('playing', () => {

	console.log("Video Start playing");
	const canvas = faceapi.createCanvasFromMedia(video);
	document.getElementById("video-inner").append(canvas);
	// document.body.append(canvas);
	const displaySize = { width: video.width, height: video.height};
	console.log(displaySize);
	faceapi.matchDimensions(canvas, displaySize);


	// detect the faces at a specific interval
	setInterval(async () => {
		if (cameraAvailability) {
			const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
			const resizedDetections = faceapi.resizeResults(detections, displaySize);
			canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
			faceapi.draw.drawDetections(canvas, resizedDetections);
			// console.log(detections);
			if(detections.length > 1){
				noPersonFound();
			}else if(detections.length == 1){
				personAbsence = 0;
			}else{
				noPersonFound();
			}
		}
	}, 1000);

})

