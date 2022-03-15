
var i = 0;
function typeWriter() {
    var txt_opt1 = "Buzzer";
    var txt_opt2 = "Music";
    var txt_footer = "Created by JJA, 2022.";
    while (i < txt_opt1.length + txt_opt2.length + txt_footer.length) {
        if (i < txt_opt1.length) {
          document.getElementById("typed_banner3").innerHTML += txt_opt1.charAt(i);
          console.log(i)
          i++;
          setTimeout(typeWriter, 1000);
        } else if (i < txt_opt1.length + txt_opt2.length) {
          document.getElementById("typed_banner4").innerHTML += txt_opt2.charAt(i - txt_opt1.length);
          i++;
          setTimeout(typeWriter, 1000);
        } else if (i < txt_opt1.length + txt_opt2.length + txt_footer.length) {
          document.getElementById("typed_banner_footer").innerHTML += txt_footer.charAt(i - txt_opt1.length - txt_opt2.length);

          i++;
          setTimeout(typeWriter, 1000);
        }
    }
}