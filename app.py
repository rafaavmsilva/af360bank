from flask import Flask, redirect, render_template

app = Flask(__name__)

@app.route('/redirect/<project>')
def redirect_to_subdomain(project):
    if project == 'comissoes':
        return redirect('https://sistema-de-comissoes.onrender.com')
    elif project == 'financeiro':
        return redirect('https://projeto-financeiro.onrender.com')
    return redirect('/')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)