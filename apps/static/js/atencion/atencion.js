ups = ['224102'];

let vm = new Vue({
  el: "#appAtencion",
  delimiters: ['[[', ']]'],
  data: {
    cita: '',
    ups: '',
    paciente: '',
    servicio: 'INFECTOLOGÍA',
    current_paciente: {attributes: {}},
    datos: ''
  },
  created: function () {
    if (paciente!==undefined) {
      this.$http.get(apiURL.paciente(paciente)).then(response => {
        vm.current_paciente = response.body;
      });
    }
  },
  methods: {
    atender: function (event) {
      if (event.target.attributes.uuid_paciente){
        this.cita = '';
        this.ups = '1904';
        this.paciente = event.target.attributes.uuid_paciente.value;
        swal({
          title: 'Confirmar accion',
          text: "¿Esta seguro que desea atender al paciente?",
          type: 'warning',
          showCancelButton: true,
          confirmButtonColor: '#3085d6',
          cancelButtonColor: '#d33',
          confirmButtonText: 'Si'
        }).then(function () {
          document.getElementById('formAtencion').submit();
        });
      }
      if (event.target.attributes.uuid_cita){
        let cita = appCita.getCita(event.target.attributes.uuid_cita.value);
        this.cita = cita.uuid_cita;
        this.ups = cita.cod_ups;
        this.paciente = cita.id_phr_paciente;
        swal({
          title: 'Confirmar accion',
          text: "¿Esta seguro que desea atender al paciente?",
          type: 'warning',
          showCancelButton: true,
          confirmButtonColor: '#3085d6',
          cancelButtonColor: '#d33',
          confirmButtonText: 'Si'
        }).then(function () {
          document.getElementById('formAtencion').submit();
        });
      }
    }
  }
});
