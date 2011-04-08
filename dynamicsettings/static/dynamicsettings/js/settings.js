var original_form = null;
var settings_form_dialog_class = 'settings-form-dialog';
var reset_error_dialog_class = 'reset-error-dialog';
var helptext_dialog_class = 'helptext-types';

$(function(){
	$('.helptext-types-button').click(function(){
		$('#helptext-types').dialog({
			dialogClass: helptext_dialog_class,
			title: $('#helptext-types-title').text()
		});
	});
	
	$('.changelink').click(function(){
	   //prepare the form first
	   var setting_key = $(this).attr('id').replace('change-', '');
	   var setting_value = $(['#value-', setting_key].join('')).text();
	   var setting_type = $(['#type-', setting_key].join('')).text();
	   initSettingsForm(setting_key, setting_value, setting_type);
	})
	
	$('.deletelink').click(function(){
	   var setting_key = $(this).attr('id').replace('reset-', '');
	   //need this for the csrf token
	   $('#reset-error-form form #id_key').attr('value', setting_key);
	   $.post($('#reset-error-form form').attr('action'), $('#reset-error-form form').serialize(), function(response){
	   	   var response_json = $.parseJSON(response);
		   if (response_json['status'] === 'success') {
				//change db setting icon
				$(['#indb-', setting_key].join('')).hide();
				$(['#notindb-', setting_key].join('')).show();
				//change back to original value
				$(['#value-', setting_key].join('')).text(response_json['value']);
				//change back to original type
				$(['#type-', setting_key].join('')).text(response_json['type']);
		   }
		   else {
		   	  $('#reset-error-content').text(response_json['message']);
		   	  $('#reset-error-content').dialog({
			        dialogClass: reset_error_dialog_class,
			        title: $('#reset-error-title').text()
			  })
		   }
	   })
	});
});

function initSettingsForm(setting_key, setting_value, setting_type) {
	if (original_form === null) {
		original_form = $('.settings-form-cont').html();
	}
	//1. put key into form key field and disable it
	$('.settings-form-cont #id_key').attr({
		'value': setting_key,
		'readonly': 'readonly',
		'disabled': 'disabled'
	});
	//2. put value in form value field
	$('.settings-form-cont #id_value').text(setting_value);
	var type_option_elem = $(['.settings-form-cont #id_type option[value="', setting_type, '"]'].join(''));
	//3. if type is not NoneType put select type for type selection and disable it
	type_option_elem.attr('selected', 'selected');
	if (setting_type!=='NoneType'){
		$('.settings-form-cont #id_type').attr({
		   'readonly': 'readonly',
		   'disabled': 'disabled'
		});
	}
	else {
		$('.settings-form-cont #id_type').removeAttr('disabled');
		$('.settings-form-cont #id_type').removeAttr('readonly');
	}
	//4. show the dialog
	$('.settings-form-cont').dialog({
		dialogClass: settings_form_dialog_class,
		title: $('#settings-form-title').text()
	})
	//5. bind submit handler to form so it will not redirect
	initSettingsSubmit(settings_form_dialog_class, setting_key, setting_value, setting_type);
}

function initSettingsSubmit(dialog_class, setting_key, setting_value, setting_type) {
	$(['.', dialog_class, ' #settings-form'].join('')).submit(function(){
       //first enable the form elements again, so they can be serialized
       $('.settings-form-cont #id_key').removeAttr('disabled');
       $('.settings-form-cont #id_type').removeAttr('disabled');
       var target = $(this).attr('action');
       var serialized_form = $(this).serialize();
       $.post(target, serialized_form, function(response){
          var response_json = $.parseJSON(response);
          if (response_json['status'] === 'success') {
		  	$(['#notindb-', setting_key].join('')).hide();
		  	$(['#indb-', setting_key].join('')).show();
		  	$(['#value-', setting_key].join('')).text(response_json['value']);
			$(['#type-', setting_key].join('')).text(response_json['type']);
		  	$('.settings-form-cont').dialog('close');
			$('.settings-form-cont').remove();
			$('#settings-form-container').append('<div class="settings-form-cont"></div>');
			$('.settings-form-cont').html(original_form);
		  }
		  else {
		  	$('.settings-form-cont').dialog('close');
			$('.settings-form-cont').remove();
			$('#settings-form-container').append('<div class="settings-form-cont"></div>');
		  	$('.settings-form-cont').html(response_json['form']);
		  	initSettingsForm(setting_key, setting_value, setting_type);
		  }
       })
       return false;
   })
}
