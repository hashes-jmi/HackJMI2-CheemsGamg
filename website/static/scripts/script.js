// video things
const video = document.querySelector("#videoElement");
const showVideo = document.querySelector("#stop");
const icon = document.querySelector("#stop .btn");

function stop() {
    let stream = video.srcObject;
    let tracks = stream.getTracks();
    for (let i=0; i<tracks.length; i++) { tracks[i].stop(); }
    video.srcObject = null;
    icon.classList.remove('fa-video');
    icon.classList.add('fa-video-slash');
    showVideo.style.backgroundColor = 'rgb(255, 117, 117)';
}

function start(){
    if(navigator.mediaDevices.getUserMedia){
        navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => video.srcObject = stream)
        .catch(() => {
            console.log("Something went wrong!");
            alert("Could not start the camera");
        });
    }
    else{ alert("Could not start the camera"); }
    icon.classList.remove('fa-video-slash');
    icon.classList.add('fa-video');
    showVideo.style.backgroundColor = 'white';
}

showVideo.addEventListener("click", () => {
    if(video.srcObject != null){ stop(); }
    else{ start(); };
});


// Camera things
const capture = document.querySelector("#capture .btn");
const canvas = document.querySelector("#canvas");
const input = document.getElementById('imageInput')

capture.addEventListener('click', function() {
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    let img_src;
    if(video.srcObject != null){ 
        img_src = canvas.toDataURL('image/jpeg'); 
        input.setAttribute('value', img_src);
        console.log(img_src);
    }
});