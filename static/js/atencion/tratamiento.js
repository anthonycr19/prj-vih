$("#id_med4, #id_med5, #id_med6").select2({
  theme: "bootstrap",
  minimumInputLength: 5,
  ajax: {
    url: apiURL.medicamentos,
    dataType: 'json',
    delay: 500,
    cache: true,
    data: function (params) {
      return {
        q: params.term
      };
    },
    processResults: function (data, params) {
      return {
        results: data.results.map(function (m) {
          return {
            id: m.id,
            text: m.descripcion
          }
        })
      }
    }
  }
}).on('select2:select', function (evt) {
  $('#extra_tarv').removeClass('hidden');
  let sel = $(evt.target);
  if (evt.target.id === 'id_med4') {
    $('#div-3-med').removeClass('hidden');
    $('#id_tarv-3-medicamento').val(sel.val());
    $('#label-3-med').html(sel.find('option:selected').text());
  } else if (evt.target.id === 'id_med5') {
    $('#div-4-med').removeClass('hidden');
    $('#id_tarv-4-medicamento').val(sel.val());
    $('#label-4-med').html(sel.find('option:selected').text());
  } else if (evt.target.id === 'id_med6') {
    $('#div-5-med').removeClass('hidden');
    $('#id_tarv-5-medicamento').val(sel.val());
    $('#label-5-med').html(sel.find('option:selected').text());
  }
});
let m1 = $("#id_med1").select2({
  theme: "bootstrap",
  minimumInputLength: 5,
  ajax: {
    url: apiURL.antiretrovirales,
    dataType: 'json',
    delay: 500,
    cache: true,
    data: function (params) {
      return {
        m1: params.term
      };
    },
    processResults: function (data, params) {
      return {
        results: data.results.map(function (m) {
          return {
            id: m.id,
            text: m.descripcion
          }
        })
      }
    }
  }
}).on('select2:select', function (evt) {
  $('#id_tarv-0-medicamento').val(m1.val());
  $('#label-0-med').html(m1.find('option:selected').text());
  $('#div-0-med').find('input').attr('required', 'required');
});
let m2 = $("#id_med2").select2({
  theme: "bootstrap",
  minimumInputLength: 5,
  ajax: {
    url: apiURL.antiretrovirales,
    dataType: 'json',
    delay: 500,
    cache: true,
    data: function (params) {
      return {
        m1: m1.val(),
        m2: params.term
      };
    },
    processResults: function (data, params) {
      return {
        results: data.results.map(function (m) {
          return {
            id: m.id,
            text: m.descripcion
          }
        })
      }
    }
  }
}).on('select2:select', function (evt) {
  $('#id_tarv-1-medicamento').val(m2.val());
  $('#label-1-med').html(m2.find('option:selected').text());
  $('#div-1-med').find('input').attr('required', 'required');
});
let m3 = $("#id_med3").select2({
  theme: "bootstrap",
  minimumInputLength: 5,
  ajax: {
    url: apiURL.antiretrovirales,
    dataType: 'json',
    delay: 500,
    cache: true,
    data: function (params) {
      return {
        m1: m1.val(),
        m2: m2.val(),
        m3: params.term,
      };
    },
    processResults: function (data, params) {
      return {
        results: data.results.map(function (m) {
          return {
            id: m.id,
            text: m.descripcion
          }
        })
      }
    }
  }
}).on('select2:select', function (evt) {
  $('#id_tarv-2-medicamento').val(m3.val());
  $('#label-2-med').html(m3.find('option:selected').text());
  $('#div-2-med').find('input').attr('required', 'required');
});
