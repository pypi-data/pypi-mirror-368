var win = Ext.getCmp('{{ component.client_id }}');
var form = win.getForm();
var logsPeriodEndField = form.findField('logs_period_ended_at');

// Устанавливаем текущую дату и время как максимальное значение
// и выполняем валидацию каждую секунду
var validationInterval = setInterval(function() {
    logsPeriodEndField.setMaxValue(new Date())
    logsPeriodEndField.validate();
}, 1000);

win.on('destroy', function() {
    clearInterval(validationInterval);
});
