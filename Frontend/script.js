// Footer copyright stuff
const footer = document.querySelector('footer');
const date = new Date().getFullYear();
footer.innerHTML = `<p>Copyright &copy; ${date} &nbsp; HackJMI | Cheems Gamg</p>`;


// video things
const video = document.querySelector("#videoElement");
const showVideo = document.querySelector("#stop");
const icon = document.querySelector("#btn");

function stop() {
    let stream = video.srcObject;
    let tracks = stream.getTracks();
  
    for (let i=0; i<tracks.length; i++) {
      let track = tracks[i];
      track.stop();
    }
    video.srcObject = null;
    icon.classList.remove('fa-video');
    icon.classList.add('fa-video-slash');
    showVideo.style.backgroundColor = 'rgb(255, 117, 117)';
}

function start(){
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream;
        })
        .catch(() => {
            console.log("Something went wrong!");
            alert("Could not start the camera");
        });
    }
    else{
        alert("Could not start the camera");
    }
    icon.classList.remove('fa-video-slash');
    icon.classList.add('fa-video');
    showVideo.style.backgroundColor = 'white';
}

showVideo.addEventListener("click", () => {
    if(video.srcObject != null){
        stop();
    }
    else{
        start();
    };
});
