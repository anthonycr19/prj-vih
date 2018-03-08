$(document).ready(function () {
  var baseUrl = '/api/v1/';
  var urls = {
    'departamentos': baseUrl + 'departamentos/',
    'provincias': baseUrl + 'provincias/',
    'distritos': baseUrl + 'distritos/',
    'localidades': baseUrl + 'localidades/',
  };

  var $NacimientoPais = $('#id_nacimiento_pais');
  var $idDepartamento = $('#id_departamento');
  var $idProvincia = $('#id_provincia');
  var $idDistrito = $('#id_distrito');
  var $nombreDep = $('#id_departamento_nombre');
  var $nombreProv = $('#id_provincia_nombre');
  var $nombreDist = $('#id_distrito_nombre');

  function buildSelect(data) {
    return data.map(function (elem) {
      return '<option value="' + elem.codigo +'" >' + elem.nombre + '</option>';
    }).join('');
  }

  $NacimientoPais.on('change', function () {
    var selectedOption = $(this).find('option:selected').val();
    if (selectedOption == 177) {
      var url = urls.departamentos;
      $.getJSON(url, function (res) {
        $idDepartamento.html(buildSelect(res.data));
        $idDepartamento.trigger('change');
      });
    }else{
      $idDepartamento.find('option').remove();
      $idDepartamento.val('');
      $idProvincia.find('option').remove();
      $idProvincia.val('');
      $idDistrito.find('option').remove();
      $idDistrito.val('');
    }
  });

  $idDepartamento.on('change', function () {
    var selectedOption = $(this).find('option:selected').val();
    if (selectedOption.length) {
      var url = urls.provincias + selectedOption;
      $.getJSON(url, function (res) {
        $idProvincia.html(buildSelect(res.data));
        $idProvincia.trigger('change');
      });
    }else{
      $idProvincia.find('option').remove();
      $idProvincia.val('');
      $idDistrito.find('option').remove();
      $idDistrito.val('');
    }
  });

  $idProvincia.on('change', function () {
    $nombreDep.val($('#id_departamento :selected').text());
    $nombreProv.val($('#id_provincia :selected').text());
    $nombreDist.val($('#id_distrito :selected').text());

    var departamento_id = $idDepartamento.find('option:selected').val();
    var selectedOption = $(this).find('option:selected').val();
    if (selectedOption.length) {
      var url = urls.distritos + departamento_id + '/' +selectedOption;
      $.getJSON(url, function (res) {
        $idDistrito.html(buildSelect(res.data));
      });
    }else{
      $idDistrito.find('option').remove();
      $idDistrito.val('');
    }
  });

  $('#form-brigada').submit(function (event) {
    $('#btn-guardar').prop('disabled', true);
    $nombreDep.val($('#id_departamento :selected').text());
    $nombreProv.val($('#id_provincia :selected').text());
    $nombreDist.val($('#id_distrito :selected').text());
    $idDepartamento.val($('#id_departamento').val());
    $idProvincia.val($('#id_provincia').val());
    $idDistrito.val($('#id_distrito').val());
  });
});
