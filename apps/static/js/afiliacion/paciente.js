let appPaciente = new Vue({
  el: '#appPaciente',
  delimiters: ['[[', ']]'],
  data: {
    pacientes: [],
    paciente: {attributes: {}},
    nombre_paciente: [],
    list_buscar_paciente: [],
    loading: false,
    url: apiURL.crearconsejeriapost,
    url_listar_resultado_examen: apiURL.listar_resultado_examen,
  },
  methods: {
    getPacientes: function (e) {
      let q = e.target.value;
      if (q.length >= 5) {
        let apiResource = this.$resource(apiURL.pacientes);
        this.pacientes = [];
        apiResource.query({q: q}).then(response => {
          appPaciente.pacientes = response.body.data;
        });
      } else {
        this.pacientes = [];
      }
    },
    getPaciente: function (e) {
      let i = parseInt(e.target.parentNode.parentNode.childNodes[0].innerHTML) - 1;
      return this.pacientes[i];
    },
    buscarPaciente: function (e) {
      let url = apiURL.buscar_paciente + '?q=' + this.nombre_paciente;
      this.$http.get(url, {
        before: () => {
          this.loading = true;
        }
      })
      .then(response => {
        this.list_buscar_paciente = response.body.data;
      })
      .then(() => {
        this.loading = false;
      });
    },
  }
});
