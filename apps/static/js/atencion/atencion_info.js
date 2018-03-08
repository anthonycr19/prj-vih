let vm = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    servicio: '',
    cie_personal: '',
    cie_familiar: '',
    current_paciente: {attributes: {}}
  },
  beforeMount: function () {
    if (paciente!==undefined) {
      this.$http.get(apiURL.paciente(paciente)).then(response => {
        vm.current_paciente = response.body;
      });
    }
  },
});
