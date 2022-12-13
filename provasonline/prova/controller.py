from provasonline import db, login_required
from provasonline.prova.models.Prova import Opcao, Pergunta, Prova, Resposta, AlunoProva
from provasonline.turma.models.Turma import Turma, AlunoTurma
from provasonline.aluno.models.Aluno import Aluno
from provasonline.professor.models.Professor import Professor
from provasonline.utilities.string_treat import *
from provasonline.constants import usuario_urole_roles
from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user
from datetime import datetime, date

class PorcentagemNegativa(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

prova = Blueprint('prova', __name__, template_folder='templates')

@prova.route("/cadastrar_prova", methods=["GET","POST"])
@login_required(role=[usuario_urole_roles['PROFESSOR']])
def cadastrar_prova():
    valor_total = 0

    if request.method == 'POST':
        descricao = request.form['prova']
        descricao = remove_espacos_texto(descricao)
        temporizada = transforma_um_e_zero_em_bool(request.form['temporizada'])

        tempo = request.form['tempo']

        data      = datetime.strptime(request.form['data'], '%Y-%m-%d').date()

        # if (not data_no_futuro(data)):
            # flash("Aviso: A data da prova cadastrada se encontra no passado.")

        turma = request.form['turma']

        prova = Prova(data, descricao, 0, current_user.id, turma, temporizada, tempo)
        db.session.add(prova)
        db.session.commit()

        numero_de_perguntas = request.form['numero_de_perguntas']

        contador = 0

        while (contador < int(numero_de_perguntas)):
            pergunta = request.form['pergunta'+str(contador)]
            valor    = request.form['valor'+str(contador)]

            valor_total = valor_total + int(valor)

            questao = Pergunta(pergunta, prova.id, valor)
            db.session.add(questao)
            db.session.commit()

            opcao1   = request.form['opcao'+str(contador)+'1']
            opcao2   = request.form['opcao'+str(contador)+'2']
            opcao3   = request.form['opcao'+str(contador)+'3']
            opcao4   = request.form['opcao'+str(contador)+'4']

            correta  = int(request.form['correta'+str(contador)])

            alternativa1 = Opcao(opcao1, False, questao.id)
            alternativa2 = Opcao(opcao2, False, questao.id)
            alternativa3 = Opcao(opcao3, False, questao.id)
            alternativa4 = Opcao(opcao4, False, questao.id)

            seleciona_alternativa_correta(alternativa1, alternativa2, alternativa3, alternativa4, correta)

            db.session.add(alternativa1)
            db.session.add(alternativa2)
            db.session.add(alternativa3)
            db.session.add(alternativa4)

            contador = contador + 1

        prova.valor = valor_total

        db.session.commit() 
        flash("Prova cadastrada com sucesso")
        return redirect(url_for('prova.listar_provas'))

    turmas = Turma.query.filter(Turma.id_professor == current_user.id)
    return render_template("cadastrar_prova.html", turmas = turmas)

@prova.route("/ver_prova_correta/<_id>", methods=["GET","POST"])
@login_required(role=[usuario_urole_roles['PROFESSOR']])
def ver_prova_correta(_id):
    prova = Prova.query.get_or_404(_id)
    return render_template("ver_prova_correta.html", prova = prova)

@prova.route("/listar_provas", methods=["GET","POST"])
@login_required()
def listar_provas():
    provas = Prova.query.all()
    
    #print(f"Provas: {provas}")
    #print("\n")
    #print("\n")

    if current_user.urole == 'aluno':
        provas = (AlunoTurma.query.join(Turma, Turma.id == AlunoTurma.turma_id)
                                .join(Prova, Prova.turma == Turma.id)
                                .outerjoin(AlunoProva, Prova.id == AlunoProva.prova_id)
                                .add_columns((Prova.id).label("prova_id"),
                                            (Prova.descricao).label("descricao"),
                                            (Prova.data).label("data"),
                                            (Prova.valor).label("valor"),
                                            (AlunoProva.nota).label("nota"),
                                            (Turma.nome).label("turma"),
                                            (AlunoProva.data_entrega).label("data_entrega"),
                                            (Prova.tempo).label("tempo"),
                                            (Turma.descricao).label("turma_descricao"))
                                .filter(AlunoTurma.aluno_id == current_user.id)).all() 
        #print(f"Provas2: {provas}")
        percentuais = adicionar_percentual(provas)
        atrasadas = adicionar_entregas_atrasadas(provas)
        #print(f"Formato de uma prova: {provas[0]}")

        return render_template("listar_provas.html", provas = provas, percentual = percentuais, atrasadas = atrasadas)
    else:
        provas = (Professor.query.join(Turma, Turma.id_professor == Professor.id)
                                .join(Prova, Prova.turma == Turma.id)
                                .add_columns((Prova.id).label("prova_id"),
                                            (Prova.descricao).label("descricao"),
                                            (Prova.data).label("data"),
                                            (Prova.valor).label("valor"),
                                            (Turma.nome).label("turma"),
                                            (AlunoProva.data_entrega).label("data_entrega"),
                                            (Prova.tempo).label("tempo"),
                                            (Turma.descricao).label("turma_descricao"))
                                .filter(Professor.id == current_user.id)).all() 

    return render_template("listar_provas.html", provas = provas)




@prova.route("/listar_notas", methods=["GET","POST"])
@login_required()
def listar_notas():
    provas = Prova.query.all()

    provas = (AlunoTurma.query.join(Turma, Turma.id == AlunoTurma.turma_id)
                                .join(Prova, Prova.turma == Turma.id)
                                .outerjoin(AlunoProva, Prova.id == AlunoProva.prova_id)
                                .add_columns((Prova.id).label("prova_id"),
                                            (Prova.descricao).label("descricao"),
                                            (Prova.data).label("data"),
                                            (Prova.valor).label("valor"),
                                            (AlunoProva.nota).label("nota"),
                                            (AlunoProva.data_entrega).label("data_entrega"),
                                            (Prova.tempo).label("tempo"),
                                            (Turma.nome).label("turma"),
                                            (Turma.descricao).label("turma_descricao"))
                                .filter(AlunoTurma.aluno_id == current_user.id)).all()

    melhores_provas = melhores_notas(provas)
    provasComNota0 = provas_que_zerei(provas)

    return render_template("listar_notas.html", melhores = melhores_provas, zeradas = provasComNota0)

@prova.route("/responder_prova/<_id>", methods=["GET","POST"])
@login_required(role=[usuario_urole_roles['ALUNO']])
def responder_prova(_id):
    prova = Prova.query.get_or_404(_id)  
    turma = Turma.query.get_or_404(prova.turma)    

    if AlunoProva.query.filter(AlunoProva.prova_id == _id, AlunoProva.aluno_id == current_user.id).first():
        return redirect(url_for('prova.ver_correcao', id_prova = _id, id_aluno = current_user.id)) 

    if request.method == 'POST':
        nota = 0
        for p in prova.perguntas: 
            opcao = request.form['op'+str(p.id)]
            
            aux = Opcao.query.get_or_404(opcao)

            if (aux.correta == 1):
                resposta = Resposta(_id, p.id, opcao, 1, current_user.id) 
                nota = nota + p.valor
            else:
                resposta = Resposta(_id, p.id, opcao, 0, current_user.id)

            db.session.add(resposta)

        aluno_prova = AlunoProva(current_user.id, _id, nota)
        db.session.add(aluno_prova)

        db.session.commit()

        flash("Prova respondida com sucesso!")
        return redirect(url_for('prova.prova_respondida', _id = _id))  

    return render_template("responder_prova.html", prova = prova, turma = turma)

@prova.route("/prova_respondida/<_id>", methods=["GET","POST"])
@login_required()
def prova_respondida(_id):
    # TODO: PEGAR RESPOSTA DA PROVA DO ALUNO E MOSTRAR NOTA E CORREÇÃO
    prova = Prova.query.get_or_404(_id)
    respostas = Resposta.query.filter(Resposta.prova == _id).all() # filtrar pelo aluno tb
    return render_template("prova_respondida.html", prova = prova, respostas = respostas)

@prova.route("/ver_correcao/<id_prova>/<id_aluno>", methods=["GET","POST"])
@login_required()
def ver_correcao(id_prova, id_aluno):
    prova = Prova.query.get_or_404(id_prova)
    turma = Turma.query.get_or_404(prova.turma) 
    respostas = Resposta.query.filter(Resposta.prova == id_prova, Resposta.aluno == id_aluno).all()
    nota = nota_da_prova(respostas)
    porcentagem = nota_para_porcentagem(prova.valor, nota)

    return render_template("ver_correcao.html", prova = prova, respostas = respostas, nota = nota, turma = turma, percentual = nota)

def data_no_futuro(dateI, today = date.today()):
    result = True
    if dateI < today:
        result = False

    return result

def seleciona_alternativa_correta(alternativa1, alternativa2, alternativa3, alternativa4, alternativaCorreta):
    if (alternativaCorreta == 1):
        alternativa1.correta = True
    elif (alternativaCorreta == 2):
        alternativa2.correta = True
    elif (alternativaCorreta == 3):
        alternativa3.correta = True
    else:
        alternativa4.correta = True

def corrige_questao(resposta):
    acertou = False
    if resposta.acertou:
        acertou = True

    return acertou

def nota_da_prova(respostas):
    nota = 0
    for resposta in respostas:
        if corrige_questao(resposta):
            nota = nota + resposta.pergunta_obj.valor

    return nota

def remove_espacos_texto(texto):
    return texto.strip()

def melhores_notas(provas):
    zeradas = provas_que_zerei(provas)
    provas = remove_provas_que_zerei(provas, zeradas)
    newlist = sorted(provas, key=lambda x: x.nota, reverse=True)
    return newlist

def remove_provas_que_zerei(melhores_provas, provas_que_zerei):
    melhores_provas = set(melhores_provas)
    provas_que_zerei = set(provas_que_zerei)
    difference = [x for x in melhores_provas if x not in provas_que_zerei]
    return difference

def provas_que_zerei(provas):
    result = []
    for prova in provas:
        if prova.nota == 0:
            result.append(prova)
    
    return result

def adicionar_percentual(provas):
    percentuais = []
    for i in range(len(provas)):
        aux = provas[i].valor
        porcetagem = nota_para_porcentagem(aux if aux != 0 else 1, provas[i].nota)
        porcetagem = formatar_para_porcentagem(porcetagem)
        percentuais.append(porcetagem)

    return percentuais

def formatar_para_porcentagem(valor):

    if valor < 0:
        raise PorcentagemNegativa("Porcentagem Negativa!")
    valor = str(round(valor, 2))
    valor = str(valor) + '%'
    return valor

def nota_para_porcentagem(total, parcial):
    nota = 0
    if parcial == None:
        parcial = 0
    try:
        nota = (100 * parcial) / total
    except ZeroDivisionError:
        nota = -1
        #print("Divisao por zero!!")
        raise ZeroDivisionError
    
    except TypeError:
        nota = -1
        raise TypeError


    return nota

def adicionar_entregas_atrasadas(provas):
    entregas = []
    for i in range(len(provas)):
        atrasada = prova_entrega_atrasada(provas[i].tempo, provas[i].data_entrega)
        entregas.append(atrasada)

    return entregas

def prova_entrega_atrasada(data_limite, data_entrega):

    if (data_limite is None):
        return False
    if (data_entrega is None):
        return False

    data_limite = data_limite
    data_entrega = data_entrega
    result = False

    try:
        if (data_entrega <= data_limite):
            result = False
        else:
            result = True
    
    except TypeError:
        raise TypeError

    return result

def quantidadeDeTurmasDoAluno(provas) -> int:
    aux = []
    for prova in provas:
        aux.append(prova.turma)
    result = len(list(set(aux)))
    return result