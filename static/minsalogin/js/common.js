/**
 * Created by cj on 3/31/17.
 */
function alertMessage(title, message, type='success') {
  swal({
    title: title,
    html: message,
    type: type
  });
  NProgress.done();
}

function get_data_api(url) {
  var json_data = null;
  $.ajax({
    async: false,
    global: false,
    url: url,
    dataType: "json",
    success: function (data) {
      json_data = data.data;
    }
  });
  NProgress.done();
  return json_data;
}
