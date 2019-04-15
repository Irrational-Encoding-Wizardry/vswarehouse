$(function() {
    $(".project-installer").click(function() {
        var el = document.createElement("textarea");
        el.value = $(this).attr("data-copy-text");
        document.body.appendChild(el);
        el.style.position = "absolute";
        el.style.left = "-99999px";
        el.select();
        document.execCommand("copy");
        document.body.removeChild(el);

        $.notify({
            "message": "A command has been copied to your clipboard.<br>Enter this command into your commandline."
        }, {"type": "success", "delay": 3000})
    });
});