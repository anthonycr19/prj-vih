$(document).ready(function () {
  $('.date_picker').find('input').datepicker({
    changeMonth: true,
    changeYear: true,
    yearRange: "-100Y:+0Y",
    maxDate: 0
  });

  var $tipoDocumento = $('#id_tipo_documento');
  var $numeroDocumento = $('#id_numero_documento');

  function evaluarTipoDocumento(val){
    if( val == 2 || val == 3 || val == 4 || val == 5 || val == 6 || val == 7){
      $numeroDocumento.prop('disabled', false);
    }else{
      $numeroDocumento.prop('disabled', true);
      $numeroDocumento.val('');
    }
  }

  $tipoDocumento.on('change', function () {
    evaluarTipoDocumento($(this).val());
  });
});
