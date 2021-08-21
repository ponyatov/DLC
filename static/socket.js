const sio = io();

sio.on('connect', (msg) => {
    console.log('sio', 'connect', msg);
})

sio.on('localtime', (msg) => {
    console.log('sio', 'localtime', msg);
    $('#localtime').html(`${msg.date} | ${msg.time}`)
})

sio.on("reload", (msg) => {
    console.log('sio', 'reload', msg);
    document.location.reload();
})
