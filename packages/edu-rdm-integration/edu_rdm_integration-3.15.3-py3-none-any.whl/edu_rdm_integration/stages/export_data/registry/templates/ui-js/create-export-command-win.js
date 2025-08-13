var win = Ext.getCmp('{{ component.client_id }}');
var form = win.getForm();
var periodEndField = form.findField('period_ended_at');

// Устанавливаем текущую дату и время как максимальное значение
// и выполняем валидацию каждую секунду
var validationInterval = setInterval(function() {
    periodEndField.setMaxValue(new Date())
    periodEndField.validate();
}, 1000);

win.on('destroy', function() {
    clearInterval(validationInterval);
});
