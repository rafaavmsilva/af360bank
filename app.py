from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/redirect/<project>')
def redirect_to_subdomain(project):
    if project == 'comissoes':
        return redirect('https://comissoes.af360bank.online')
    elif project == 'financeiro':
        return redirect('https://financeiro.af360bank.online')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
