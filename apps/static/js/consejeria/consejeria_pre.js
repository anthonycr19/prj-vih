let cita_row = null;
let consejeriaPre = {
  cita: null,
  paciente: null,
  medico: null,
  eess: null,
  tipo_poblacion: 1,
  consejeria_previa: false,
  esta_consentido: false,
  validacion: ''
};
ups = ['224102'];

let vm = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    consejeria_datos: [],
    hoy: moment().format("YYYY-MM-DD"),
    servicio: '',
    paciente: {attributes: {}},
    pacientes: [],
    current_paciente: {attributes: {}},
    consejerias_pre: [],
    consejeria_pre: consejeriaPre,
    consejeria: {
      consejeria: {}
    },
    cita: {},
    examen_solicitado: {},
    examenes_solicitados: [],
    examenes: []
  },
  mounted() {
    $("#id_fecha_prueba").datepicker({
      changeMonth: true,
      changeYear: true,
      regional: "es",
      dateFormat: "dd/mm/yy",
      showOtherMonths: true,
      selectOtherMonths: true,
      showAnim: "slideDown",
      onSelect: function (dateText) {
        vm.examen_solicitado.fecha = dateText;
      }
    });
    $("#id_cptname").autocomplete({
      minLength: 3,
      select: function (event, ui) {
        document.getElementById('id_cpt').value = vm.examen_solicitado.cpt = ui.item.id;
      },
      appendTo: "#md_solicitud_laboratorio_form",
      autoFocus: true,
      scroll: true,
      source: function (request, response) {
        datos = request.term;
        $.get({
          url: apiURL.cpts,
          data: {'q': datos},
          success: function (data) {
            response(data.map(function (c) {
              return {
                id: c.attributes.codigo_cpt,
                label: c.attributes.denominacion_procedimiento,
                value: c.attributes.denominacion_procedimiento
              };
            }));
          }
        });
      }
    });
  },
  methods: {
    getExamenesLaboratorioPaciente: function (e) {
      let apiResource = this.$resource(apiURL.laboratioresultado);
      this.examenes = [];
      apiResource.query({laboratorio_examen__paciente: this.cita.id_phr_paciente}).then(response => {
        vm.examenes = response.body.results;
      });
    },
    solicitarExamenLaboratorio: function (e) {
      let apiResource = this.$resource(apiURL.laboratorioexamenes);
      swal({
        title: 'Confirmar accion',
        text: "¿Esta seguro que desea solicitar este examen de laboratorio?",
        type: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Si'
      }).then(function () {
        let frm_lab = document.getElementById('frm_laboratorio');
        let frm = new FormData(frm_lab);
        apiResource.save(frm).then(response => {
          vm.examenes_solicitados.push(response.body);
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
          swal('Ups!', 'Ha ocurrido un error! <br>' + msg, 'success');
        });
      });
    },
    getConsejeria: function (e) {
      cita_row = e.target.parentNode.parentNode;
      this.cita = appCita.getCita(e.target.id);
      this.consejerias_pre = consejeriaPre;
      this.consejeria_pre.cita = this.cita.uuid_cita;
      this.consejeria_pre.paciente = this.cita.id_phr_paciente;
      this.consejeria_pre.medico = this.cita.numero_documento_medico;
      this.consejeria_pre.eess = this.cita.cod_eess;
      this.consejeria_pre.ups = this.cita.cod_ups;
      this.$http.get(apiURL.ciudadano(this.cita.id_phr_paciente)).then(response => {
        vm.current_paciente = response.body.data;
      });
      this.consejerias_pre = [];
      let apiResource = this.$resource(apiURL.consejeriapre);
      apiResource.query({consejeria__atencion__paciente: this.cita.id_phr_paciente}).then(response => {
        vm.consejerias_pre = response.body['results'];
      });
    },
    crearConsejeriaPre: function (e) {
      let apiResource = this.$resource(apiURL.consejeriapre);
      swal({
        title: 'Confirmar registro',
        text: '¿Esta seguro que desea registrar esta consejeria?',
        type: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Si'
      }).then(function () {
        let frm = new FormData();
        Object.keys(vm.consejeria_pre).forEach(function (key) {
          frm.append(key, vm.consejeria_pre[key]);
        });
        apiResource.save(frm).then(response => {
          vm.consejeria_datos = response.data.data;
          cita_row.childNodes[5].innerHTML = 'Atendido';
          swal(
            'Exito!',
            'La consejeria fue registrada exitosamente.',
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
    }
  }
});
