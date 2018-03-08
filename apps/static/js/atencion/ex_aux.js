$(".dateinput").datepicker({
  changeMonth: true,
  changeYear: true
});
$("#id_imagen, #id_laboratorio, #id_procedimiento").select2({
  theme: "bootstrap",
  minimumInputLength: 5,
  ajax: {
    url: apiURL.cpts,
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
        results: data.map(function (m) {
          return {
            id: m.attributes.codigo_cpt,
            text: m.attributes.denominacion_procedimiento
          }
        })
      }
    }
  }
});
