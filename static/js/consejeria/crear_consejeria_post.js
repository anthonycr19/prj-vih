let cita_row = null;

ups = ['224102'];

let vm = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    url_editar_post: apiURL.editarconsejeriapost,
    url_eliminar_post: apiURL.eliminarconsejeriapost,
    servicio: '',
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
    cod_ups: '',
    datos_paciente: [],
  },
  mounted:function(){
    this.mostrarFormulario();
  },
  methods: {
    mostrarFormulario: function (e) {
      let apiResource = this.$resource(apiURL.laboratioresultado);
      this.$http.get(apiURL.cita(cita_uuid)).then(response => {
        this.cita = response.body;
        this.consejeria.id = null;
        this.pacienteID = this.cita.id_phr_paciente;
        this.citaID = this.cita.uuid_cita;
        this.cod_ups =  this.cita.cod_ups;
        this.$http.get(apiURL.ciudadano(this.cita.id_phr_paciente)).then(response => {
          vm.current_paciente = response.body.data;
        });
      });
      this.examenes = [];
      apiResource.query({laboratorio_examen__paciente: this.cita.id_phr_paciente}).then(response => {
        vm.examenes = response.body.results;
      });
      this.$http.get(apiURL.consejeriapost, {consejeria__atencion__paciente: this.cita.id_phr_paciente}).then(response => {
        vm.consejerias = response.body.results;
      });
    },
    eliminar: function (e) {
      let var_consejeria = this.consejerias;
      swal({
        title: 'Confirmar accion',
        text: "¿Esta seguro que desea eliminar este registro?",
        type: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Si'
      }).then(function () {

        $.ajax({
          url: '/eliminar-post-consejeria/'+e.id,
          success: function(data){
            if (data.resultado == 'OK')
            {
              swal(
                'Registro eliminado!!!', data.detalle,
                'success'
              );
              var index = var_consejeria.indexOf(e);
              var_consejeria.splice(index, 1);
            }
            else
            {
              swal(
                'Error al eliminar!', data.detalle,
                'error'
              )
            }
          },
          error: function(err) {
            swal(
              'Error al eliminar!', data.detalle,
              'error'
            );
          }
        });
      });
    },
  },
});
