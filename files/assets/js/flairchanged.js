const flairchanged = document.getElementById('flairchanged').value
const date = formatDate(new Date(flairchanged*1000));
const text = ` - Your flair has been locked until ${date}`;
document.getElementById('flair-body').value += text;
