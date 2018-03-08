$(document).ready(function () {
  var loadForm = function () {
    var btn = $(this);
    var url =  btn.attr("data-url");
    $("#modal-contactofamiliar").modal("show");
    $.get(url, function(data) {
      $("#modal-contactofamiliar .modal-content").html(data)
    });
  };

  $(".js-crear-contactofamiliar").click(loadForm);
});
