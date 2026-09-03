document.addEventListener('DOMContentLoaded', async function () {
    const calendarEl = document.getElementById('calendar');

    // 祝日データをAPIから取得
    const response = await fetch('https://holidays-jp.github.io/api/v1/date.json');
    const holidayData = await response.json();

    // 祝日データをイベント形式に変換
    const holidays = Object.entries(holidayData).map(([date, name]) => ({
        title: name,
        date: date,
        backgroundColor: '#d9534f', // 祝日の色（薄い黄色）
        textColor: '#fff'           // 文字色を黒
    }));

    // Pythonから渡されたデータをマージ
    const allEvents = [...events, ...holidays];

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'ja', // カレンダーを日本語化
        events: allEvents, // 祝日を含むイベントデータ
        dayCellDidMount: function(info) {
            const day = info.date.getDay();
            const dateString = formatDate(info.date); // 'YYYY-MM-DD'形式の文字列を取得

            // 日曜・土曜の色付け
            if (day === 0) {
                info.el.style.backgroundColor = '#ffe6e6'; // 日曜日 - 薄い赤
            } else if (day === 6) {
                info.el.style.backgroundColor = '#e6f7ff'; // 土曜日 - 薄い青
            }

            // 祝日の日付限定で色付け
            const holiday = holidays.find(h => h.date === dateString); // 祝日がその日かどうかを確認
            if (holiday) {
                info.el.style.backgroundColor = '#ffe6e6'; // 祝日の色（薄い黄色）
            }
        },
        eventClick: function(info) {
            alert(`タイトル: ${info.event.title}\n詳細: ${info.event.extendedProps.description || 'なし'}`);
        },
        headerToolbar: {
            left: 'prev,next',
            center: 'title',
            right: 'today'
        }
    });

    calendar.render();

    // 日付を 'YYYY-MM-DD' 形式で返すヘルパー関数
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); // 月は0から始まるので +1
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
});
