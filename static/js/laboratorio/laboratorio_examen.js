let listaExamenes = {
  cinombre_cpt: null,
  fecha: null,
  observaciones: '',
  estado: '',
};


let vm = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
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
      minLength: 0,
      select: function (event, ui) {
        document.getElementById('id_cpt').value = vm.examen_solicitado.cpt = ui.item.id;
      },
      appendTo: "#frm_laboratorio",
      autoFocus: true,
      scroll: true,
      source: function (request, response) {
        $.get({
          url: apiURL.cpts,
          success: function (data) {
            response(data.map(function (c) {
              return {
                id: c.procedimiento_codigo,
                label: c.procedimiento_nombrecorto,
                value: c.procedimiento_nombrecorto
              };
            }));
          }
        });
      }
    });
  },
  data: {
    url_eliminar_examen: apiURL.eliminarexamen,
    pacientes: [],
    paciente: '',
    examen_solicitado: {},
    examenes_solicitados: [],
    lista_examenes_solicitados: [],
  },
  methods: {
    getExamenesLaboratorio: function (e) {
      let apiResource = this.$resource(apiURL.laboratioresultado);
      this.examenes = [];
      apiResource.query({laboratorio_examen__paciente: e.target.id}).then(response => {
        vm.examenes = response.body.results;
      });

      let apiResourceExamenes = this.$resource(apiURL.laboratorioexamenes);
      apiResourceExamenes.query({paciente: e.target.id}).then(response => {
        vm.examenes_solicitados = response.body['results'];
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
          swal('Ups!', 'Ha ocurrido un error! <br>' + msg, 'error');
        });
      });
    },
    prepareSolicitud: function (e) {
      this.getExamenesLaboratorio(e);
      this.paciente = e.target.id;
    },

    eliminar: function (e) {
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
        url: '/eliminar-examen/'+e.id,
        type: "POST",
        cache: false,
        success: function(data){
          if (data.resultado === 'OK')
          {
            swal(
              'Registro eliminado!!!', data.detalle,
              'success'
            );
            var index = vm.examenes_solicitados.indexOf(e);
            vm.examenes_solicitados.splice(index, 1);
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
      }).catch(swal.noop);
    },


  }
});
