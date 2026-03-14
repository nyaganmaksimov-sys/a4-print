const canvas = document.getElementById('wheelCanvas');
const ctx = canvas.getContext('2d');
const spinButton = document.getElementById('spinButton');
const resultDiv = document.getElementById('result');

// Настройки секторов (Цвета и призы)
const segments = [
    { label: '10%', description: 'Скидка 10% на этот заказ!', color: '#FF6B6B' },
    { label: '20%', description: 'Скидка 20% на этот заказ!', color: '#4ECDC4' },
    { label: '5 Фото', description: '+5 фото 10x15 в подарок!', color: '#45B7D1' },
    { label: 'Ламинация', description: 'Ламинирование в подарок!', color: '#96CEB4' },
    { label: '30% след.', description: 'Купон: 30% на следующий заказ!', color: '#FFE194' },
    { label: 'ДЖЕКПОТ', description: '🎉 ЗАКАЗ БЕСПЛАТНО (до 500₽)! 🎉', color: '#F7D794' }
];

let currentAngle = 0; // Текущий угол поворота колеса
let isSpinning = false;
let spinTimeout = null;

// Рисуем колесо
function drawWheel(angle) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const arc = (Math.PI * 2) / segments.length;
    
    for (let i = 0; i < segments.length; i++) {
        const startAngle = i * arc + angle;
        const endAngle = (i + 1) * arc + angle;
        
        // Рисуем сектор
        ctx.beginPath();
        ctx.fillStyle = segments[i].color;
        ctx.moveTo(canvas.width / 2, canvas.height / 2);
        ctx.arc(canvas.width / 2, canvas.height / 2, canvas.width / 2 - 10, startAngle, endAngle);
        ctx.closePath();
        ctx.fill();
        
        // Рисуем обводку
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(canvas.width / 2, canvas.height / 2);
        ctx.arc(canvas.width / 2, canvas.height / 2, canvas.width / 2 - 10, startAngle, endAngle);
        ctx.closePath();
        ctx.stroke();
        
        // Добавляем текст
        ctx.save();
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate(startAngle + arc / 2);
        ctx.textAlign = 'center';
        ctx.fillStyle = '#000';
        ctx.font = 'bold ' + (canvas.width / 20) + 'px "Segoe UI"';
        ctx.fillText(segments[i].label, canvas.width / 4, 10);
        ctx.restore();
    }
    
    // Рисуем центральный круг (стрелка)
    ctx.beginPath();
    ctx.fillStyle = '#333';
    ctx.arc(canvas.width / 2, canvas.height / 2, 20, 0, 2 * Math.PI);
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 3;
    ctx.stroke();
    
    // Рисуем указатель (стрелку сверху)
    ctx.fillStyle = '#ff0';
    ctx.beginPath();
    ctx.moveTo(canvas.width / 2 - 15, 5);
    ctx.lineTo(canvas.width / 2, 25);
    ctx.lineTo(canvas.width / 2 + 15, 5);
    ctx.fill();
}

// Функция для определения выигрыша
function getPrize(angle) {
    const rawAngle = angle % (Math.PI * 2); // Нормализуем угол от 0 до 2PI
    const segmentAngle = (Math.PI * 2) / segments.length;
    
    // Индекс сектора (учитываем, что указатель сверху)
    let index = Math.floor(((Math.PI * 2) - rawAngle) / segmentAngle) % segments.length;
    
    // Корректировка для правильного сектора (из-за точки отсчета)
    if (rawAngle < 0.1) index = 0; 
    
    return segments[index];
}

// Функция вращения
function spinWheel() {
    if (isSpinning) return;
    
    isSpinning = true;
    spinButton.disabled = true;
    
    const spinTime = 4000; // 4 секунды вращения
    const spinAngle = Math.random() * 20 + 15; // Случайное число оборотов (от 15 до 35)
    const startTime = Date.now();
    const startAngle = currentAngle;
    
    function animateSpin() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / spinTime, 1);
        
        // Эффект замедления (ease-out)
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        currentAngle = startAngle + (spinAngle * Math.PI * 2) * easeProgress;
        
        drawWheel(currentAngle);
        
        if (progress < 1) {
            spinTimeout = requestAnimationFrame(animateSpin);
        } else {
            // Колесо остановилось
            isSpinning = false;
            spinButton.disabled = false;
            
            // Определяем приз
            const prize = getPrize(currentAngle);
            resultDiv.innerHTML = `🎁 <strong>ТВОЙ ПРИЗ:</strong> ${prize.description}`;
            resultDiv.style.background = '#d4edda';
            resultDiv.style.border = '2px solid #28a745';
            
            // Сохраняем результат в localStorage, если нужно (для статистики)
            console.log('Выигрыш:', prize.description);
        }
    }
    
    animateSpin();
}

// Инициализация
drawWheel(currentAngle);

// Слушаем клик по кнопке и по canvas (для удобства)
spinButton.addEventListener('click', spinWheel);
canvas.addEventListener('click', spinWheel);

// Адаптивность при изменении размера окна (перерисовка)
window.addEventListener('resize', () => {
    drawWheel(currentAngle);
});
