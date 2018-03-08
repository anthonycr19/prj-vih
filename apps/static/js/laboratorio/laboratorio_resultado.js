let i = null;
let vm = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    current_paciente: {
      attributes: {
        sexo: '0'
      }
    },
    showModal: false,
    examenes: [],
    pacientes: [],
    examen_solicitado: {},
    examenes_solicitados: [],
    paciente: '',
    laboratorio_examen: '',
    laboratorio_resultado_examen: '',
    fecha_resultado: '',
    fecha_resultado_editar: '',
    nro_prueba: '',
    resultado: '',
    nro_muestra: '',
    observacion: '',
    url_eliminar_resultado: apiURL.eliminar_resultado_examen,
  },
    mounted() {
      $("#id_fecha_resultado").datepicker({
        changeMonth: true,
        changeYear: true,
        regional: "es",
        dateFormat: "yy-mm-dd",
        showOtherMonths: true,
        selectOtherMonths: true,
        showAnim: "slideDown",
        onSelect: function (dateText) {
          this.fecha_resultado = dateText;
        }
      });
  },
  methods: {
    getExamenesLaboratorio: function (e) {
      let apiResource = this.$resource(apiURL.laboratioresultado);
      this.examenes = [];
      this.current_paciente = appPaciente.getPaciente(e);
      apiResource.query({laboratorio_examen__paciente: e.target.id}).then(response => {
        vm.examenes = response.body.results;
      });

      let apiResourceExamenes = this.$resource(apiURL.laboratorioexamenes);
      apiResourceExamenes.query({paciente: e.target.id}).then(response => {
        vm.examenes_solicitados = response.body['results'];
      });
    },
    getExamen: function (e) {
      this.examen_solicitado = {id: e};
      this.laboratorio_examen = e;
    },
    getResultadoEditar: function (idexamen, idresultado) {
      let pk = idresultado;
      this.laboratorio_examen = idexamen;
      this.laboratorio_resultado_examen = idresultado;
      this.$http.get(apiURL.resultado_examen(pk)).then(response => {
        this.fecha_resultado_editar = response.body.fecha_resultado;
        this.nro_prueba = response.body.nro_prueba;
        this.resultado = response.body.resultado;
        this.nro_muestra = response.body.nro_muestra;
        this.observacion = response.body.observacion;
      });
    },
    setLimpiarResultadoGuardar: function () {
      this.fecha_resultado_editar = '';
      this.laboratorio_resultado_examen = '';
      this.laboratorio_examen = '';
      this.nro_prueba = '';
      this.resultado = '';
      this.nro_muestra = '';
      this.observacion = '';
    },
    setExamen: function (e) {
      let pk = this.examen_solicitado.id;
      this.laboratorio_examen = pk
      swal({
        title: 'Confirmar accion',
        text: "¿Esta seguro que desea registrar este resultado?",
        type: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Si'
      }).then(function () {
        let frm = document.getElementById('frm_resultado');
        let data = new FormData(frm);
        vm.$http.post(`/api/v1/examenes/crear-resultado/`, data).then(response => {
          swal(
            'Exito!',
            'La solicitud de examen de laboratorio fue registrada exitosamente.',
            'success'
          );
        }, response => {
          let msg = '';
          if (response.status === 400) {
            let errors = JSON.parse(response.bodyText);
            Object.keys(errors).forEach(function (key) {
              msg = msg + '<strong>' + key.replace(/\b\w/g, l => l.toUpperCase()) + ': ' + '</strong>' + errors[key] + '<br>';
            });
          }
          swal('Ups!', 'Ha ocurrido un error! <br>' + msg, 'error');
        });
      });
    },
    setResultadoGuardar: function (e) {
      let id_resultado_examen = document.forms['frm_editar_resultado']['laboratorio_resultado_examen'].value;
      swal({
        title: 'Confirmar accion',
        text: "¿Esta seguro que desea registrar este resultado?",
        type: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Si'
      }).then(function () {
        let frm = document.getElementById('frm_editar_resultado');
        let data = new FormData(frm);
        vm.$http.put(`/api/v1/examenes/editar-resultado/${id_resultado_examen}/`, data).then(response => {
          swal(
            'Exito!',
            'La solicitud de examen de laboratorio fue registrada exitosamente.',
            'success'
          );
        }, response => {
          let msg = '';
          if (response.status === 400) {
            let errors = JSON.parse(response.bodyText);
            Object.keys(errors).forEach(function (key) {
              msg = msg + '<strong>' + key.replace(/\b\w/g, l => l.toUpperCase()) + ': ' + '</strong>' + errors[key] + '<br>';
            });
          }
          swal('Ups!', 'Ha ocurrido un error! <br>' + msg, 'error');
        });
      });
    },
    prepareSolicitud: function (e) {
      this.getExamenesLaboratorio(e);
      this.paciente = e.target.id;
    }
  }
});
