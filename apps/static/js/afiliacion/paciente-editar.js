$(document).ready(function () {
  $('.date_picker').find('input').datepicker({
    changeMonth: true,
    changeYear: true,
    yearRange: "-100Y:+0Y",
    maxDate: 0
  });

  function calcularEdad(f_actual, f_nacimiento){
    var difDuracion = moment.duration(f_actual.diff(f_nacimiento));
    var msg = '';
    if(difDuracion.years() >= 1){
      msg += difDuracion.years() + ' años ' + difDuracion.months() + ' meses ' + difDuracion.days()+ ' dias'
    }else{
      msg += difDuracion.months() + ' meses ' + difDuracion.days()+ ' dias'
    }
    return msg ;
  }

  var $fecha_nacimiento = $('#id_fecha_nacimiento'),
    $edad = $('#id_edad'),
    fecha_nacimiento,
    fecha_actual;

  $fecha_nacimiento.on('change', function () {
    fecha_nacimiento = moment($fecha_nacimiento.val(), 'DD/MM/YYYY');
    fecha_actual = moment();
    $edad.val(calcularEdad(fecha_actual, fecha_nacimiento));
  });

  var $numeroDocumento = $('#id_numero_documento');
  var $numeroHCE = $('#id_numero_hce');
  var $apellido_paterno = $('#id_apellido_paterno');
  var $apellido_materno = $('#id_apellido_materno');
  var $nombres = $('#id_nombres');
  var $nacimiento_pais = $('#id_nacimiento_pais');
  var $nacimiento_departamento = $('#id_nacimiento_departamento');
  var $nacimiento_provincia = $('#id_nacimiento_provincia');
  var $nacimiento_distrito = $('#id_nacimiento_distrito');
  var $residencia_pais = $('#id_residencia_pais');
  var $residencia_departamento = $('#id_residencia_departamento');
  var $residencia_provincia = $('#id_residencia_provincia');
  var $residencia_distrito = $('#id_residencia_distrito');
  var $fecha_nacimiento = $('#id_fecha_nacimiento');
  var $sexo = $('#id_sexo');
  var $tipo_documento = $('#id_tipo_documento');
  var $direccion = $('#id_direccion');
  var $id_paciente = $('#id_paciente');

  $tipo_documento.attr('readonly', true);
  $numeroDocumento.attr('readonly', true);
  $numeroHCE.attr('readonly', true);
  if ($nombres.val() == '') {
    $nombres.attr('readonly', false);
  }
  else{
    $nombres.attr('readonly', true);
  }

  if ($apellido_paterno.val() == '') {
    $apellido_paterno.attr('readonly', false);
  }
  else{
    $apellido_paterno.attr('readonly', true);
  }

  if ($apellido_materno.val() == '') {
    $apellido_materno.attr('readonly', false);
  }
  else{
    $apellido_materno.attr('readonly', true);
  }

  if ($numeroHCE.val() == '') {
    $numeroHCE.attr('readonly', false);
    $numeroHCE.val($numeroDocumento.val());
  }
  else{
    $numeroHCE.attr('readonly', true);
  }

  $sexo.attr('readonly', true);
  $nacimiento_pais.attr('readonly', true);
  $nacimiento_departamento.attr('readonly', true);
  $nacimiento_provincia.attr('readonly', true);
  $nacimiento_distrito.attr('readonly', true);
  $residencia_pais.attr('readonly', true);
  $residencia_departamento.attr('readonly', true);
  $residencia_provincia.attr('readonly', true);
  $residencia_distrito.attr('readonly', true);
  $fecha_nacimiento.attr('readonly', true);
  $direccion.attr('readonly', true);

  $.get('/afiliacion/familia-paciente/'+$numeroDocumento.val(), function(data) {
    $('#datos_familia').html(data);
  });

  //Obtener provincia, distritos de PHr

  var baseUrl = '/api/v1/';
  var urls = {
    'departamentos': baseUrl + 'departamentos/',
    'provincias': baseUrl + 'provincias/',
    'distritos': baseUrl + 'distritos/',
    'localidades': baseUrl + 'localidades/',
  };

  var $pai_res_actual = $('#id_residencia_actual_pais');
  var $dep_res_actual = $('#id_residencia_actual_departamento');
  var $pro_res_actual = $('#id_residencia_actual_provincia');
  var $dis_res_actual = $('#id_residencia_actual_distrito');
  var $loc_res_actual = $('#id_centro_poblado_actual');


  function buildSelect(data) {
    return data.map(function (elem) {
      return '<option value="' + elem.codigo + '">' + elem.nombre + '</option>';
    }).join('');
  }

  $pai_res_actual.on('change', function () {
    var selectedOption = $(this).find('option:selected').val();
    if (selectedOption == 177) {
      var url = urls.departamentos;
      $.getJSON(url, function (res) {
        $dep_res_actual.html(buildSelect(res.data));
        $dep_res_actual.trigger('change');
      });
    }else{
      $dep_res_actual.find('option').remove();
      $dep_res_actual.val('');
      $pro_res_actual.find('option').remove();
      $pro_res_actual.val('');
      $dis_res_actual.find('option').remove();
      $dis_res_actual.val('');
    }
  });

  $dep_res_actual.on('change', function () {
    var selectedOption = $(this).find('option:selected').val();
    if (selectedOption.length) {
      var url = urls.provincias + selectedOption;
      $.getJSON(url, function (res) {
        $pro_res_actual.html(buildSelect(res.data));
        $pro_res_actual.trigger('change');
      });
    }else{
      $pro_res_actual.find('option').remove();
      $pro_res_actual.val('');
      $dis_res_actual.find('option').remove();
      $dis_res_actual.val('');
    }
  });

  $pro_res_actual.on('change', function () {
    var departamento_id = $dep_res_actual.find('option:selected').val();
    var selectedOption = $(this).find('option:selected').val();
    if (selectedOption.length) {
      var url = urls.distritos + departamento_id + '/' + selectedOption;
      $.getJSON(url, function (res) {
        $dis_res_actual.html(buildSelect(res.data));
      });
    }else{
      $dis_res_actual.find('option').remove();
      $dis_res_actual.val('');
    }
  });

  $dis_res_actual.on('change', function () {
    var departamento_id = $dep_res_actual.find('option:selected').val();
    var provincia_id = $pro_res_actual.find('option:selected').val();
    var selectedOption = $(this).find('option:selected').val();
    if (selectedOption.length) {
      var url = urls.localidades + departamento_id + '/' + provincia_id + '/' + selectedOption;
      $.getJSON(url, function (res) {
        $loc_res_actual.html(buildSelect(res.data));
      });
    }else{
      $dis_res_actual.find('option').remove();
      $dis_res_actual.val('');
    }
  });
});

function put_coords(lat, long){
  $('#id_latitud').val(lat);
  $('#id_longitud').val(long);
}
$('#id_latitud').attr('readonly', true);
$('#id_longitud').attr('readonly', true);
$('#ifrCoordenada').attr('src','/api/v1/coordenada/'+$('#id_latitud').val()+'/'+$('#id_longitud').val());
