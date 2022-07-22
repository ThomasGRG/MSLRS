$(function () {
    $(".sidebar-link").click(function () {
     $(".sidebar-link").removeClass("is-active");
     $(this).addClass("is-active");
    });
   });
   
   $(window)
    .resize(function () {
     if ($(window).width() > 1090) {
      $(".sidebar").removeClass("collapse");
     } else {
      $(".sidebar").addClass("collapse");
     }
    })
    .resize();
   
  //  const allVideos = document.querySelectorAll(".video");
   
  //  allVideos.forEach((v) => {
  //   v.addEventListener("mouseover", () => {
  //    const video = v.querySelector("video");
  //    video.play();
  //   });
  //   v.addEventListener("mouseleave", () => {
  //    const video = v.querySelector("video");
  //    video.pause();
  //   });
  //  });
   
   $(function () {
    $(".logo, .logo-expand, .discover").on("click", function (e) {
     $(".main-container").removeClass("show");
     $(".main-container").scrollTop(0);
    });
    $(".trending, .video").on("click", function (e) {
     $(".main-container").addClass("show");
     $(".main-container").scrollTop(0);
     $(".sidebar-link").removeClass("is-active");
     $(".trending").addClass("is-active");
    });
  });
   
  //   $(".video").click(function () {
  //    var source = $(this).find("source").attr("src");
  //    var title = $(this).find(".video-name").text();
  //    var person = $(this).find(".video-by").text();
  //    var img = $(this).find(".author-img").attr("src");
  //    $(".video-stream video").stop();
  //    $(".video-stream source").attr("src", source);
  //    $(".video-stream video").load();
  //    $(".video-p-title").text(title);
  //    $(".video-p-name").text(person);
  //    $(".video-detail .author-img").attr("src", img);
  //   });
  //  });






   

/*
function getUserMedia(options, successCallback, failureCallback) {
  var userMedia = navigator.getUserMedia || navigator.webkitGetUserMedia ||
    navigator.mozGetUserMedia || navigator.msGetUserMedia;
  if (userMedia) {
    return userMedia.bind(navigator)(options, successCallback, failureCallback);
  }
}

function getStream (type) {
  if (!navigator.getUserMedia && !navigator.webkitGetUserMedia &&
    !navigator.mozGetUserMedia && !navigator.msGetUserMedia) {
    alert('User Media not supported.');
    return;
  }

  var options = {"video":true};
  getUserMedia(options, success, failure);
}

function success(stream){
    var mediaControl = document.querySelector('video');
    if (navigator.mozGetUserMedia) {
      mediaControl.mozSrcObject = stream;
    } else {
      mediaControl.srcObject = stream;
      mediaControl.src = (window.URL || window.webkitURL).createObjectURL(stream);
    }
}

function failure(err)
{
    alert('Error: ' + err);	
}
*/
// document.getElementById('start').addEventListener('click', function(){
//     //getStream('video');
//     var constraints = { audio: false, video: true }
//     navigator.mediaDevices.getUserMedia(constraints)
//     .then(function(stream) {
//       var video = document.querySelector('video');
//       video.srcObject = stream;
//       video.onloadedmetadata = function(e) {
//         video.play();
//       };
//     })
//     .catch(function(err) {
//       /* handle the error */
//       alert(err.message);
//     });
  
//   });
  
  // document.getElementById('log').addEventListener('click', function(){
  //   navigator.mediaDevices.enumerateDevices()
  //   .then(function(devices) {
  //     devices.forEach(function(device) {
  //       console.log(device.kind + ": " + device.label +
  //                   " id = " + device.deviceId);
  //     });
  //   })
  //   .catch(function(err) {
  //     console.log(err.name + ": " + err.message);
  //   });
  // });
  
  
  // document.getElementById('stop').addEventListener('click', function(){
  //   var video = document.querySelector('video');
  //   var stream = video.srcObject;
  //   var tracks = stream.getTracks();
  
  //   tracks.forEach(function(track) {
  //     track.stop();
  //   });
  
  //   video.srcObject = null;
  // });