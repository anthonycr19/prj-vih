let cita_row = null;

ups = ['224102'];

let vm = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    servicio: 'CONSULTA EXTERNA-PSICOLOGÍA-CONSEJERÍA',
    hoy: moment().format("YYYY-MM-DD"),
    pacientes: [],
    paciente: {attributes: {}},
    current_paciente: {attributes: {}},
    consejerias: [],
    consejeria: {
      consejeria: {}
    },
    examenes: [],
    via_transmision: 'sexual',
    tipo_transmision: 'NODETERMINADO',
    pacienteID: '',
    citaID: '',
    cita: {},
    cod_ups: ''
  },
  methods: {
    mostrarFormulario: function (e) {
      let apiResource = this.$resource(apiURL.laboratioresultado);
      this.cita = appCita.getCita(e.target.id);
      this.examenes = [];
      this.$http.get(apiURL.ciudadano(this.cita.id_phr_paciente)).then(response => {
        vm.current_paciente = response.body.data;
      });
      apiResource.query({laboratorio_examen__paciente: this.cita.id_phr_paciente}).then(response => {
        vm.examenes = response.body.results;
      });
      this.$http.get(apiURL.consejeriapost, {consejeria__atencion__paciente: this.cita.id_phr_paciente}).then(response => {
        vm.consejerias = response.body.results;
      });
      this.consejeria.id = null;
      this.pacienteID = this.cita.id_phr_paciente;
      this.citaID = this.cita.uuid_cita;
      this.cod_ups =  this.cita.cod_ups;
    }
  }
});
