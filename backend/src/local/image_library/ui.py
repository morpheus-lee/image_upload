PAGE = """<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>圖片管理 · Superset</title>
  <link rel="stylesheet" href="{{ url_for(endpoint ~ '.stylesheet') }}">
</head>
<body>
  <header><a href="{{ url_for('Superset.welcome') }}">← 返回 Superset</a></header>
  <main>
    <div class="heading"><h1>圖片管理</h1><span>{{ count }} 張圖片</span></div>
    {% if error %}<p class="notice error" role="alert">{{ error }}</p>{% endif %}
    {% if uploaded %}<p class="notice" role="status">圖片已上傳。</p>{% endif %}
    {% if can_upload %}
      <form action="{{ url_for(endpoint ~ '.upload') }}" method="post" enctype="multipart/form-data">
        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
        <div>
          <label for="image">選擇圖片</label>
          <input id="image" type="file" name="image" accept="image/jpeg,image/png,image/webp"
            aria-describedby="limits" required>
          <small id="limits">JPEG、PNG 或 WebP 靜態圖片，最多 10 MiB、2,000 萬像素。</small>
        </div>
        <button type="submit">上傳圖片</button>
      </form>
    {% endif %}
    {% if rows %}
      <div class="table-wrap">
        <table aria-label="已上傳圖片">
          <thead><tr><th scope="col">縮圖</th><th scope="col">檔名</th><th scope="col">上傳時間（台北）</th></tr></thead>
          <tbody>
          {% for row in rows %}
            <tr>
              <td><img src="{{ url_for(endpoint ~ '.thumbnail', image_id=row.id) }}"
                width="72" height="54" loading="lazy" alt=""></td>
              <td><a href="{{ url_for(endpoint ~ '.image', image_id=row.id) }}" target="_blank"
                rel="noopener">{{ row.name }}</a></td>
              <td><time datetime="{{ row.created_at }}">{{ row.display_time }}</time></td>
            </tr>
          {% endfor %}
          </tbody>
        </table>
      </div>
      {% if last_page > 1 %}
      <nav aria-label="圖片列表分頁">
        {% if page > 1 %}
          <a href="{{ url_for(endpoint ~ '.library', page=page - 1) }}">上一頁</a>
        {% endif %}
        <span>第 {{ page }} / {{ last_page }} 頁</span>
        {% if page < last_page %}
          <a href="{{ url_for(endpoint ~ '.library', page=page + 1) }}">下一頁</a>
        {% endif %}
      </nav>
      {% endif %}
    {% else %}
      <p class="empty">目前沒有圖片。</p>
    {% endif %}
  </main>
</body>
</html>
"""

CSS = """
:root { font-family: system-ui, sans-serif; color: #162b38; background: #f5f8fa; }
body { margin: 0; }
header { background: white; border-bottom: 1px solid #dce6ea; padding: 1rem max(1rem, calc((100% - 64rem) / 2)); }
a { color: #006c83; text-underline-offset: .18em; }
main { max-width: 64rem; margin: 2.5rem auto; padding: 0 1rem; }
.heading, form, nav { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
.heading { justify-content: space-between; }
h1 { font-size: 1.8rem; }
form, .table-wrap, .empty { background: white; border: 1px solid #dce6ea; border-radius: .65rem; }
form { padding: 1rem; margin-bottom: 1.5rem; justify-content: space-between; }
label, small { display: block; }
label { font-weight: 600; margin-bottom: .45rem; }
small, .heading span { color: #475c67; }
small { margin-top: .4rem; }
input { max-width: 100%; }
button { border: 0; border-radius: .4rem; background: #006c83; color: white;
  font: inherit; font-weight: 600; padding: .55rem .9rem; cursor: pointer; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; text-align: left; }
th, td { padding: .65rem 1rem; }
th { background: #edf4f6; white-space: nowrap; }
td { border-top: 1px solid #e6edf0; overflow-wrap: anywhere; }
td:first-child { width: 4.5rem; }
td:last-child { width: 11rem; }
img { object-fit: contain; display: block; border-radius: .3rem; background: #f5f8fa; }
nav { justify-content: center; margin-top: 1rem; }
.empty, .notice { padding: 1rem; }
.notice { background: #e4f5ef; border-radius: .45rem; }
.error { background: #fce9e7; color: #7e231b; }
@media (max-width: 36rem) { th, td { padding: .55rem; } main { margin-top: 1rem; } }
"""
