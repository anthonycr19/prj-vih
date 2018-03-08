ups = ['224102'];

let vm = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    servicio: 'INFECTOLOGÍA',
    cie_personal: '',
    cie_familiar: '',
    current_paciente: {attributes: {}}
  },
  created: function () {
    if (paciente!==undefined) {
      this.$http.get(apiURL.paciente(paciente)).then(response => {
        vm.current_paciente = response.body;
      });
    }
  },
});
$("#ciePersonal").autocomplete({
  minLength: 3,
  select: function (event, ui) {
    $("#id_personal-4-cie").val(ui.item.id);
    vm.cie_personal = ui.item.value;
  },
  autoFocus: true,
  scroll: true,
  source: function (request, response) {
    datos = request.term;
    $.get({
      url: apiURL.cies,
      data: {'q': datos},
      success: function (data) {
        response(data.map(function (c) {
          return {
            id: c.attributes.id_ciex,
            label: c.attributes.desc_ciex,
            value: c.attributes.desc_ciex
          };
        }));
      }
    });
  }
});
$("#cieFamiliar").autocomplete({
  minLength: 3,
  select: function (event, ui) {
    $("#id_familiar-4-cie").val(ui.item.id);
    vm.cie_familiar = ui.item.value;
  },
  autoFocus: true,
  scroll: true,
  source: function (request, response) {
    datos = request.term;
    $.get({
      url: apiURL.cies,
      data: {'q': datos},
      success: function (data) {
        response(data.map(function (c) {
          return {
            id: c.attributes.id_ciex,
            label: c.attributes.desc_ciex,
            value: c.attributes.desc_ciex
          };
        }));
      }
    });
  }
});
$("#id_antirretroviral-med1").autocomplete({
  minLength: 3,
  select: function (event, ui) {
    $("#id_antirretroviral-medicamento1").val(ui.item.id);
  },
  autoFocus: true,
  scroll: true,
  source: function (request, response) {
    $.ajax({
      type: "GET",
      url: apiURL.antiretrovirales,
      data: {'m1': request.term},
      success: function (data) {
        response(data.results.map(function (m) {
          return {
            id: m.id,
            label: m.descripcion,
            value: m.descripcion
          }
        }));
      }
    });
  }
});
$("#id_antirretroviral-med2").autocomplete({
  minLength: 3,
  select: function (event, ui) {
    $("#id_antirretroviral-medicamento2").val(ui.item.id);
  },
  autoFocus: true,
  scroll: true,
  source: function (request, response) {
    $.ajax({
      type: "GET",
      url: apiURL.antiretrovirales,
      data: {'m1': $("#id_antirretroviral-medicamento1").val(), 'm2': request.term},
      success: function (data) {
        response(data.results.map(function (m) {
          return {
            id: m.id,
            label: m.descripcion,
            value: m.descripcion
          }
        }));
      }
    });
  }
});
$("#id_antirretroviral-med3").autocomplete({
  minLength: 3,
  select: function (event, ui) {
    $("#id_antirretroviral-medicamento3").val(ui.item.id);
  },
  autoFocus: true,
  scroll: true,
  source: function (request, response) {
    $.ajax({
      type: "GET",
      url: apiURL.antiretrovirales,
      data: {'m1': $("#id_antirretroviral-medicamento1").val(), 'm2': $("#id_antirretroviral-medicamento2").val(), 'm3': request.term},
      success: function (data) {
        response(data.results.map(function (m) {
          return {
            id: m.id,
            label: m.descripcion,
            value: m.descripcion
          }
        }));
      }
    });
  }
});
$("#id_antirretroviral-med4").autocomplete({
  minLength: 3,
  select: function (event, ui) {
    $("#id_antirretroviral-medicamento4").val(ui.item.id);
  },
  autoFocus: true,
  scroll: true,
  source: function (request, response) {
    $.ajax({
      type: "GET",
      url: apiURL.medicamentos,
      data: {'q': request.term},
      success: function (data) {
        response(data.results.map(function (m) {
          return {
            id: m.id,
            label: m.descripcion,
            value: m.descripcion
          }
        }));
      }
    });
  }
});
$("#id_antirretroviral-med5").autocomplete({
  minLength: 3,
  select: function (event, ui) {
    $("#id_antirretroviral-medicamento5").val(ui.item.id);
  },
  autoFocus: true,
  scroll: true,
  source: function (request, response) {
    $.ajax({
      type: "GET",
      url: apiURL.medicamentos,
      data: {'q': request.term},
      success: function (data) {
        response(data.results.map(function (m) {
          return {
            id: m.id,
            label: m.descripcion,
            value: m.descripcion
          }
        }));
      }
    });
  }
});
$(".dateinput").datepicker({
  changeMonth: true,
  changeYear: true
});
