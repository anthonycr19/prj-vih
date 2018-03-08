$("#id_descie").autocomplete({
  minLength: 3,
  select: function (event, ui) {
    $("#id_cie").val(ui.item.id);
  },
  autoFocus: true,
  scroll: true,
  source: function (request, response) {
    datos = request.term;
    $.get({
      url: apiURL.cies,
      data: {'q': datos},
      success: function (data) {
        let cies = data.map(function (c) {
          return {
            id: c.attributes.id_ciex,
            label: c.attributes.desc_ciex,
            value: c.attributes.desc_ciex,
            idcie: c.attributes.id_ciex
          };
        });
        response(cies);
      }
    });
  }
});
