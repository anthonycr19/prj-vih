$("#id_coinfeccion-0-cie, #id_coinfeccion-1-cie, #id_coinfeccion-2-cie").select2({
  theme: "bootstrap",
  minimumInputLength: 5,
  ajax: {
    url: apiURL.cies,
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
            id: m.attributes.id_ciex,
            text: m.attributes.desc_ciex
          }
        })
      }
    }
  }
});
$(".dateinput").datepicker({
  changeMonth: true,
  changeYear: true
});
