let lat = lng = 0;

let vm = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    paciente: {attributes: {}}
  },
  methods: {
    getPaciente: function (e) {
      let i = parseInt(e.target.parentNode.parentNode.childNodes[0].innerHTML) - 1;
      this.paciente = appPaciente.pacientes[i];
    }
  }
});

$('#aresi a').click(function (e) {
  e.preventDefault();
  $(this).tab('show');
  setTimeout(function(){ $('#map').locationpicker('autosize'); }, 500);
});

$(function () {
  $('#map').css("width", '100%').css("height", 400).locationpicker({
    location: {
      latitude: -12.043333,
      longitude: -77.028333
    },
    radius: 300,
    inputBinding: {
      locationNameInput: $('#id_referencia'),
      latitudeInput: $('#us2-lat'),
      longitudeInput: $('#us2-lon'),
      radiusInput: $('#us2-radius')
    },
    markerInCenter: true,
    enableAutocomplete: true,
    onchanged: function (currentLocation, radius, isMarkerDropped) {
      lat = currentLocation.latitude;
      lng = currentLocation.longitude;
    }
  });
});
