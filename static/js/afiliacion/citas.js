let appCita = new Vue({
  el: '#appCita',
  delimiters: ['[[', ']]'],
  created: function () {
    let url = apiURL.citas + '?fecha=' + hoy;
    this.$http.get(url).then(response => {
      this.citas_hoy = response.body.filter((c) => ups.indexOf(c.cod_ups) >= 0);
    });
    url = apiURL.citas + '?fecha_inicio=' + dias + '&fecha_fin=' + ayer;
    this.$http.get(url).then(response => {
      this.citas_pasadas = response.body.filter((c) => ups.indexOf(c.cod_ups) >= 0);
    });
  },
  data: {
    showModal: false,
    cita: {},
    list_paciente: {},
    citas_hoy: [],
    citas_pasadas: [],
    pacientes: [],
    nombre_paciente: [],
    list_buscar_paciente: [],
    loading: false,
    url_crearconsejeriapost: apiURL.crearconsejeriapost,
  },
  methods: {
    filtrarCitas: function (e) {
      let value = e.target.value;
      if (value.length < 1) {
        this.pacientes = [];
      } else {
        this.pacientes = this.citas_hoy.filter(function (element) {
          return element.paciente.numero_documento.includes(value) || element.paciente.nombre_completo.toLowerCase().includes(value.toLowerCase());
        });
      }
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
    getCita: function (uuid) {
      let citas = this.citas_hoy.filter(function (element) {
        return element.uuid_cita == uuid;
      });
      if (citas.length == 1) {
        return citas[0];
      }
      return citas;
    },
  }
});
