$(".dateinput").datepicker({
  changeMonth: true,
  changeYear: true
});
let m1 = $("#id_ram").select2({
  theme: "bootstrap",
  minimumInputLength: 5,
  ajax: {
    url: apiURL.medicamentos,
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
  $('#med_label').html(m1.find('option:selected').text());
});
function showRAM() {
  $('#ram').removeClass('hidden').find('button,input').prop("disabled", false);
}
function hiddeRAM() {
  $('#ram').addClass('hidden').find('button,input').prop("disabled", true);
}
$('#id_fg_presenta_ram_1').on('click', function (e) {
  if ($(this).is(':checked')) {
    showRAM();
  }
});
$('#id_fg_presenta_ram_2').on('click', function (e) {
  if ($(this).is(':checked')) {
    hiddeRAM();
  }
});
hiddeRAM();
