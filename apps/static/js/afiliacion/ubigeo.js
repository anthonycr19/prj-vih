$(document).ready(function () {
  var baseUrl = '/api/v1/';
  var urls = {
    'departamentos': baseUrl + 'departamentos/',
    'provincias': baseUrl + 'provincias/',
    'distritos': baseUrl + 'distritos/',
    'localidades': baseUrl + 'localidades/',
  };

  var $nacimiento_pais = $('#id_nacimiento_pais');
  var $nacimiento_departamento = $('#id_nacimiento_departamento');
  var $nacimiento_provincia = $('#id_nacimiento_provincia');
  var $nacimiento_distrito = $('#id_nacimiento_distrito');


  function buildSelect(data) {
    return data.map(function (elem) {
      return '<option value="' + elem.codigo + '">' + elem.nombre + '</option>';
    }).join('');
  }

  $nacimiento_pais.on('change', function () {
    var selectedOption = $(this).find('option:selected').val();
    if (selectedOption == 177) {
      var url = urls.departamentos;
      $.getJSON(url, function (res) {
        $nacimiento_departamento.html(buildSelect(res.data));
        $nacimiento_departamento.trigger('change');
      });
    }else{
      $nacimiento_departamento.find('option').remove();
      $nacimiento_departamento.val('');
      $nacimiento_provincia.find('option').remove();
      $nacimiento_provincia.val('');
      $nacimiento_distrito.find('option').remove();
      $nacimiento_distrito.val('');
    }
  });

  $nacimiento_departamento.on('change', function () {
    var selectedOption = $(this).find('option:selected').val();
    if (selectedOption.length) {
      var url = urls.provincias + selectedOption;
      alert(selectedOption);
      $.getJSON(url, function (res) {
        $nacimiento_provincia.html(buildSelect(res.data));
        $nacimiento_provincia.trigger('change');
      });
    }else{
      $nacimiento_provincia.find('option').remove();
      $nacimiento_provincia.val('');
      $nacimiento_distrito.find('option').remove();
      $nacimiento_distrito.val('');
    }
  });

  $nacimiento_provincia.on('change', function () {
    var departamento_id = $nacimiento_departamento.find('option:selected').val();
    var selectedOption = $(this).find('option:selected').val();
    if (selectedOption.length) {
      var url = urls.distritos + departamento_id + '/' +selectedOption;
      alert(url);
      $.getJSON(url, function (res) {
        $nacimiento_distrito.html(buildSelect(res.data));
      });
    }else{
      $nacimiento_distrito.find('option').remove();
      $nacimiento_distrito.val('');
    }
  });
});
