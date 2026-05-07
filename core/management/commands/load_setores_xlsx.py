"""
Importa a hierarquia completa de setores do CT/UFPB (4 níveis).

Hierarquia:
  Nível 0 — Centro        (tipo='centro')
  Nível 1 — Direção       (tipo='direcao')
  Nível 2 — Setores       (tipo: administrativo | departamento | coordenacao_g | coordenacao_pg)
  Nível 3 — Labs/Secr.    (tipo: laboratorio | secretaria)

Uso:
    python manage.py load_setores_xlsx          # atualiza sem apagar
    python manage.py load_setores_xlsx --limpar # apaga tudo e reimporta
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Setor

CODIGO_DIRECAO_CORRETO = '11.01.17.01'
CODIGO_DIRECAO_ANTIGO = '11.01.17.07'
CODIGO_GABINETE_CORRETO = '11.01.17.01.13'
CODIGO_GABINETE_ANTIGO = '11.01.17.07.01'

CODIGOS_RENUMERADOS = {
    CODIGO_DIRECAO_ANTIGO: CODIGO_DIRECAO_CORRETO,
    CODIGO_GABINETE_ANTIGO: CODIGO_GABINETE_CORRETO,
}


def normalizar_codigo_pai(codigo_pai):
    return CODIGOS_RENUMERADOS.get(codigo_pai, codigo_pai)


def nome_padronizado(codigo, nome, sigla):
    if codigo == '11.00.55':
        return 'CT - Centro de Tecnologia'
    if codigo == CODIGO_DIRECAO_CORRETO:
        return 'CT - DIREÇÃO DE CENTRO'

    base = ' '.join(str(nome).split())
    if base.startswith('CT - '):
        base = base[5:].strip()
    if sigla and base.startswith(f'{sigla} - '):
        base = base[len(sigla) + 3:].strip()

    return f'CT - {sigla} - {base}' if sigla else f'CT - {base}'


def migrar_codigo_antigo(codigo_antigo, codigo_correto):
    antigo = Setor.objects.filter(codigo=codigo_antigo).first()
    if not antigo:
        return
    correto = Setor.objects.filter(codigo=codigo_correto).first()
    if correto:
        Setor.objects.filter(pai=antigo).update(pai=correto)
        antigo.ativo = False
        antigo.save(update_fields=['ativo'])
        return
    antigo.codigo = codigo_correto
    antigo.save(update_fields=['codigo'])


# (codigo, nome, sigla, tipo, codigo_pai)
HIERARQUIA = [
    # ── Nível 0: Centro ──────────────────────────────────────────────────────
    ('11.00.55',    'CT - Centro de Tecnologia',          'CT',    'centro',        None),

    # ── Nível 1: Direção de Centro ───────────────────────────────────────────
    ('11.01.17.01', 'CT - DIREÇÃO DE CENTRO',              'CT-DC', 'direcao',       '11.00.55'),

    # ── Nível 2: Setores Administrativos (pai = Direção) ─────────────────────
    ('11.01.17.01.13', 'CT - GDC - Gabinete da Direção do CT',              'GDC', 'administrativo', '11.01.17.01'),
    ('11.01.17.01.08', 'CT - DC - Almoxarifado',                                       '', 'administrativo', '11.01.17.07'),
    ('11.00.55.51',    'CT - DC - Arquivo',                                             '', 'administrativo', '11.01.17.07'),
    ('11.01.17.01.09', 'CT - DC - Assessoria de Administração',                        '', 'administrativo', '11.01.17.07'),
    ('11.00.55.13',    'CT - DC - Assessoria de Extensão',                             '', 'administrativo', '11.01.17.07'),
    ('11.01.17.01.10', 'CT - DC - Assessoria de Graduação',                            '', 'administrativo', '11.01.17.07'),
    ('11.01.17.01.11', 'CT - DC - Assessoria de Planejamento',                         '', 'administrativo', '11.01.17.07'),
    ('11.01.17.22',    'CT - DC - Biblioteca Setorial',                                '', 'administrativo', '11.01.17.07'),
    ('11.00.55.58',    'CT - DC - Comissão Interna de Biossegurança',                  '', 'administrativo', '11.01.17.07'),
    ('11.00.55.66',    'CT - DC - Comissão Permanente de Sindicância',                 '', 'administrativo', '11.01.17.07'),
    ('11.01.17.01.12', 'CT - DC - Setor de Gestão de Pessoas',                         '', 'administrativo', '11.01.17.07'),
    ('11.00.55.02',    'CT - DC - Setor de Portaria',                                  '', 'administrativo', '11.01.17.07'),
    ('11.00.55.50',    'CT - DC - Secretaria',                                         '', 'administrativo', '11.01.17.07'),

    # ── Nível 2: Coordenações de Graduação (pai = Direção) ───────────────────
    ('11.01.17.23',    'CT - Coordenação de Arquitetura e Urbanismo',                  '', 'coordenacao_g',  '11.01.17.07'),
    ('11.01.17.24',    'CT - Coordenação de Engenharia Ambiental',                     '', 'coordenacao_g',  '11.01.17.07'),
    ('11.01.17.17',    'CT - Coordenação de Engenharia Civil',                         '', 'coordenacao_g',  '11.01.17.07'),
    ('11.01.17.25',    'CT - Coordenação de Engenharia de Alimentos',                  '', 'coordenacao_g',  '11.01.17.07'),
    ('11.01.17.26',    'CT - Coordenação de Engenharia de Materiais',                  '', 'coordenacao_g',  '11.01.17.07'),
    ('11.01.17.27',    'CT - Coordenação de Engenharia de Produção',                   '', 'coordenacao_g',  '11.01.17.07'),
    ('11.01.17.52',    'CT - Coordenação de Engenharia de Produção Mecânica',          '', 'coordenacao_g',  '11.01.17.07'),
    ('11.01.17.41',    'CT - Coordenação de Engenharia Mecânica',                      '', 'coordenacao_g',  '11.01.17.07'),
    ('11.01.17.42',    'CT - Coordenação de Engenharia Química',                       '', 'coordenacao_g',  '11.01.17.07'),
    ('11.01.17.43',    'CT - Coordenação do Curso de Química Industrial',              '', 'coordenacao_g',  '11.01.17.07'),
    ('11.00.55.56',    'CT - DC - Curso de Especialização em Assistência Técnica nas Áreas de Arquitetura, Urbanismo e Engenharia', '', 'coordenacao_g', '11.01.17.07'),

    # ── Nível 2: Programas de Pós-Graduação (pai = Direção) ──────────────────
    ('11.01.17.34',    'CT - Programa de Pós-Graduação em Arquitetura e Urbanismo',              'PPGAU',   'coordenacao_pg', '11.01.17.07'),
    ('11.01.17.36',    'CT - Programa de Pós-Graduação em Ciência e Tecnologia de Alimentos',   'PPGCTA',  'coordenacao_pg', '11.01.17.07'),
    ('11.01.17.33',    'CT - Programa de Pós-Graduação em Engenharia Civil e Ambiental',         'PPGECA',  'coordenacao_pg', '11.01.17.07'),
    ('11.00.55.55',    'CT - Programa de Pós-Graduação em Engenharia de Produção e Sistemas',    'PPGEPS',  'coordenacao_pg', '11.01.17.07'),
    ('11.01.17.39',    'CT - Programa de Pós-Graduação em Engenharia Mecânica',                  'PPGEM',   'coordenacao_pg', '11.01.17.07'),
    ('11.00.55.01',    'CT - Programa de Pós-Graduação em Engenharia Química',                   'PPGEQ',   'coordenacao_pg', '11.01.17.07'),
    ('11.01.17.35',    'CT - Programa Pós-Graduação em Ciência e Engenharia de Materiais',       'PPCEM',   'coordenacao_pg', '11.01.17.07'),

    # ── Nível 2: Departamentos (pai = Direção) ───────────────────────────────
    ('11.01.17.05',    'CT - Departamento de Arquitetura e Urbanismo',          'DAU',   'departamento', '11.01.17.07'),
    ('11.01.17.13',    'CT - Departamento de Engenharia Civil e Ambiental',     'DECA',  'departamento', '11.01.17.07'),
    ('11.01.17.15',    'CT - Departamento de Engenharia de Alimentos',          'DEA',   'departamento', '11.01.17.07'),
    ('11.01.17.44',    'CT - Departamento de Engenharia de Materiais',          'DEMAT', 'departamento', '11.01.17.07'),
    ('11.01.17.06',    'CT - Departamento de Engenharia de Produção',           'DEP',   'departamento', '11.01.17.07'),
    ('11.01.17.03',    'CT - Departamento de Engenharia Mecânica',              'DEM',   'departamento', '11.01.17.07'),
    ('11.01.17.14',    'CT - Departamento de Engenharia Química',               'DEQ',   'departamento', '11.01.17.07'),
    ('11.01.17.09',    'CT - Núcleo de Pesquisa e Processamento de Alimentos',  'NUPPA', 'departamento', '11.01.17.07'),

    # ── Nível 3: Laboratório da Direção de Centro ────────────────────────────
    ('11.01.17.01.07', 'CT - DC - Laboratório de Informática Gráfica', '', 'laboratorio', '11.01.17.07'),

    # ── Nível 3: DAU ─────────────────────────────────────────────────────────
    ('11.00.55.60',    'CT - DAU - Secretaria do Departamento de Arquitetura e Urbanismo', '', 'secretaria',  '11.01.17.05'),
    ('11.01.17.05.02', 'CT - DAU - Laboratório de Acessibilidade (LACESSE)',               '', 'laboratorio', '11.01.17.05'),
    ('11.00.55.23',    'CT - DAU - Laboratório de Ambiente Urbano e Edificado',            '', 'laboratorio', '11.01.17.05'),
    ('11.00.55.26',    'CT - DAU - Laboratório de Conforto Ambiental',                     '', 'laboratorio', '11.01.17.05'),
    ('11.00.55.33',    'CT - DAU - Laboratório de Estudos sobre Cidade, Cultura e Urbanidade', '', 'laboratorio', '11.01.17.05'),
    ('11.00.55.22',    'CT - DAU - Laboratório de Modelos + Prototipagem',                 '', 'laboratorio', '11.01.17.05'),
    ('11.01.17.05.01', 'CT - DAU - Laboratório de Pesquisa, Projeto e Memória',            '', 'laboratorio', '11.01.17.05'),

    # ── Nível 3: DECA ────────────────────────────────────────────────────────
    ('11.00.55.59',    'CT - DECA - Secretaria do Departamento de Engenharia Civil e Ambiental', '', 'secretaria',  '11.01.17.13'),
    ('11.00.55.24',    'CT - DECA - Laboratório de Análise Estrutural e Avaliação de Desempenho', '', 'laboratorio', '11.01.17.13'),
    ('11.01.17.13.02', 'CT - DECA - Laboratório de Eficiência Energética e Hidráulica em Saneamento (LEHNS)', '', 'laboratorio', '11.01.17.13'),
    ('11.01.17.13.07', 'CT - DECA - Laboratório de Ensaios de Materiais e Estruturas (LABEME)',  '', 'laboratorio', '11.01.17.13'),
    ('11.01.17.13.04', 'CT - DECA - Laboratório de Geotecnia e Pavimentação',                    '', 'laboratorio', '11.01.17.13'),
    ('11.01.17.13.03', 'CT - DECA - Laboratório de Hidráulica',                                  '', 'laboratorio', '11.01.17.13'),
    ('11.00.55.46',    'CT - DECA - Laboratório de Modelos Físicos Qualitativos e Computacionais','', 'laboratorio', '11.01.17.13'),
    ('11.00.55.37',    'CT - DECA - Laboratório de Pesquisa em Sistemas Ambientais Urbanos',      '', 'laboratorio', '11.01.17.13'),
    ('11.00.55.48',    'CT - DECA - Laboratório de Planejamento de Transportes',                  '', 'laboratorio', '11.01.17.13'),
    ('11.00.55.42',    'CT - DECA - Laboratório de Química Ambiental',                            '', 'laboratorio', '11.01.17.13'),
    ('11.01.17.13.01', 'CT - DECA - Laboratório de Recursos Hídricos e Engenharia Ambiental',    '', 'laboratorio', '11.01.17.13'),
    ('11.00.55.43',    'CT - DECA - Laboratório de Reologia',                                     '', 'laboratorio', '11.01.17.13'),
    ('11.01.17.13.06', 'CT - DECA - Laboratório de Saneamento Ambiental',                        '', 'laboratorio', '11.01.17.13'),
    ('11.01.17.13.05', 'CT - DECA - Laboratório de Topografia',                                  '', 'laboratorio', '11.01.17.13'),
    ('11.00.55.54',    'CT - DECA - Laboratório de Modelagem da Informação da Construção e Modelagem e Experimentação de Estruturas', '', 'laboratorio', '11.01.17.13'),
    ('11.00.55.57',    'CT - DECA - Laboratório de Análises Computacionais em Meio Ambiente',     '', 'laboratorio', '11.01.17.13'),

    # ── Nível 3: DEA ─────────────────────────────────────────────────────────
    ('11.00.55.61',    'CT - DEA - Secretaria do Departamento de Engenharia de Alimentos',        '', 'secretaria',  '11.01.17.15'),
    ('11.00.55.10',    'CT - DEA - Laboratório de Flavor',                                        '', 'laboratorio', '11.01.17.15'),
    ('11.00.55.21',    'CT - DEA - Laboratório de Apoio',                                         '', 'laboratorio', '11.01.17.15'),
    ('11.00.55.30',    'CT - DEA - Laboratório de Extração',                                      '', 'laboratorio', '11.01.17.15'),
    ('11.00.55.45',    'CT - DEA - Laboratório de Processos Microbianos em Alimentos',            '', 'laboratorio', '11.01.17.15'),
    ('11.00.55.67',    'CT - DEA - Laboratório de Engenharia Bioquímica',                         '', 'laboratorio', '11.01.17.15'),
    ('11.00.55.68',    'CT - DEA - Laboratório de Controle de Qualidade',                         '', 'laboratorio', '11.01.17.15'),
    ('11.01.17.32',    'CT - DEA - Laboratório de Análises Químicas de Alimentos',                '', 'laboratorio', '11.01.17.15'),
    ('11.01.17.15.02', 'CT - DEA - Laboratório de Bioquímica de Alimentos',                      '', 'laboratorio', '11.01.17.15'),
    ('11.01.17.15.03', 'CT - DEA - Laboratório de Engenharia de Alimentos',                      '', 'laboratorio', '11.01.17.15'),
    ('11.01.17.15.05', 'CT - DEA - Laboratório de Tecnologia de Alimentos',                      '', 'laboratorio', '11.01.17.15'),
    ('11.01.17.15.06', 'CT - DEA - Laboratório de Processamento de Derivados de Pescado',        '', 'laboratorio', '11.01.17.15'),
    ('11.01.17.15.07', 'CT - DEA - Laboratório de Análise Sensorial e Desenvolvimento de Novos Produtos', '', 'laboratorio', '11.01.17.15'),
    ('11.01.17.15.08', 'CT - DEA - Laboratório de Processamento de Derivados do Leite',          '', 'laboratorio', '11.01.17.15'),
    ('11.01.17.15.09', 'CT - DEA - Laboratório de Tecnologia de Panificação (Padaria Piloto)',   '', 'laboratorio', '11.01.17.15'),
    ('11.01.17.15.10', 'CT - DEA - Laboratório de Informática',                                  '', 'laboratorio', '11.01.17.15'),
    ('11.01.17.15.11', 'CT - DEA - Laboratório de Análises de Ácidos Graxos',                    '', 'laboratorio', '11.01.17.15'),
    ('11.01.17.15.12', 'CT - DEA - Laboratório de Processamento de Derivados de Carnes',         '', 'laboratorio', '11.01.17.15'),

    # ── Nível 3: DEMAT ───────────────────────────────────────────────────────
    ('11.00.55.63',    'CT - DEMAT - Secretaria do Departamento de Engenharia de Materiais',      '', 'secretaria',  '11.01.17.44'),
    ('11.01.17.44.06', 'CT - DEMAT - Laboratório de Caracterização Microestrutural',             '', 'laboratorio', '11.01.17.44'),
    ('11.01.17.44.02', 'CT - DEMAT - Laboratório de Cristalografia',                             '', 'laboratorio', '11.01.17.44'),
    ('11.00.55.41',    'CT - DEMAT - Laboratório de Materiais Avançados',                        '', 'laboratorio', '11.01.17.44'),
    ('11.01.17.44.05', 'CT - DEMAT - Laboratório de Materiais Cerâmicos',                       '', 'laboratorio', '11.01.17.44'),
    ('11.00.55.05',    'CT - DEMAT - Laboratório de Materiais e Biossistemas',                   '', 'laboratorio', '11.01.17.44'),
    ('11.00.55.07',    'CT - DEMAT - Laboratório de Materiais Metálicos',                        '', 'laboratorio', '11.01.17.44'),
    ('11.01.17.44.04', 'CT - DEMAT - Laboratório de Materiais Poliméricos',                     '', 'laboratorio', '11.01.17.44'),
    ('11.01.17.44.03', 'CT - DEMAT - Laboratório de Modelagem de Materiais',                    '', 'laboratorio', '11.01.17.44'),
    ('11.00.55.39',    'CT - DEMAT - Laboratório de Propriedades Mecânicas dos Materiais',       '', 'laboratorio', '11.01.17.44'),
    ('11.00.55.38',    'CT - DEMAT - Laboratório de Purificação e Aspersão de Minerais Argilosos','', 'laboratorio', '11.01.17.44'),
    ('11.00.55.40',    'CT - DEMAT - Laboratório de Química dos Materiais',                      '', 'laboratorio', '11.01.17.44'),
    ('11.01.17.44.01', 'CT - DEMAT - Laboratório de Siderurgia',                                '', 'laboratorio', '11.01.17.44'),
    ('11.00.55.47',    'CT - DEMAT - Laboratório de Solidificação Rápida',                       '', 'laboratorio', '11.01.17.44'),

    # ── Nível 3: DEP ─────────────────────────────────────────────────────────
    ('11.00.55.64',    'CT - DEP - Secretaria do Departamento de Engenharia de Produção',         '', 'secretaria',  '11.01.17.06'),
    ('11.00.55.25',    'CT - DEP - Laboratório de Análise do Trabalho',                           '', 'laboratorio', '11.01.17.06'),
    ('11.01.17.06.01', 'CT - DEP - Laboratório de Métodos Quantitativos Aplicados',              '', 'laboratorio', '11.01.17.06'),
    ('11.01.17.06.02', 'CT - DEP - Laboratório de Desenvolvimento de Produtos e Inovação',       '', 'laboratorio', '11.01.17.06'),
    ('11.01.17.06.03', 'CT - DEP - Laboratório de Engenharia de Sustentabilidade e Consumo',     '', 'laboratorio', '11.01.17.06'),
    ('11.01.17.06.04', 'CT - DEP - Laboratório de Simulação de Processo Discreto',               '', 'laboratorio', '11.01.17.06'),
    ('11.01.17.06.05', 'CT - DEP - Laboratório de Informática',                                  '', 'laboratorio', '11.01.17.06'),

    # ── Nível 3: DEM ─────────────────────────────────────────────────────────
    ('11.00.55.62',    'CT - DEM - Secretaria do Departamento de Engenharia Mecânica',            '', 'secretaria',  '11.01.17.03'),
    ('11.00.55.04',    'CT - DEM - Laboratório de Carvão Ativado',                               '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.06',    'CT - DEM - Laboratório de Inovação e Conversão Térmica',                 '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.08',    'CT - DEM - Laboratório de Automação e Controle',                         '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.11',    'CT - DEM - Laboratório de Energia Sustentável',                          '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.12',    'CT - DEM - Laboratório de Conformação Mecânica',                         '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.27',    'CT - DEM - Laboratório de Controle de Vibração e Ruído',                 '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.28',    'CT - DEM - Laboratório de Dinâmica',                                     '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.29',    'CT - DEM - Laboratório de Instrumentação e Controle',                    '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.31',    'CT - DEM - Laboratório de Engenharia de Precisão',                       '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.32',    'CT - DEM - Laboratório de Ensaios Mecânicos',                            '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.34',    'CT - DEM - Laboratório de Mecatrônica',                                  '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.35',    'CT - DEM - Laboratório de Metalografia',                                 '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.36',    'CT - DEM - Laboratório de Metrologia Dimensional',                       '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.44',    'CT - DEM - Laboratório de Representação Gráfica',                        '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.49',    'CT - DEM - Laboratório de Transferência de Calor e Massa',               '', 'laboratorio', '11.01.17.03'),
    ('11.00.55.53',    'CT - DEM - Laboratório de Atividades Meteorológicas',                    '', 'laboratorio', '11.01.17.03'),
    ('11.01.17.03.03', 'CT - DEM - Laboratório de Máquinas e Acionamentos Elétricos',           '', 'laboratorio', '11.01.17.03'),
    ('11.01.17.03.04', 'CT - DEM - Laboratório de Motores de Combustão Interna',                '', 'laboratorio', '11.01.17.03'),
    ('11.01.17.03.05', 'CT - DEM - Laboratório de Oficina Mecânica',                            '', 'laboratorio', '11.01.17.03'),
    ('11.01.17.03.06', 'CT - DEM - Laboratório de Refrigeração e Ar Condicionado',              '', 'laboratorio', '11.01.17.03'),
    ('11.01.17.03.07', 'CT - DEM - Laboratório de Solidificação Rápida',                        '', 'laboratorio', '11.01.17.03'),
    ('11.01.17.03.08', 'CT - DEM - Laboratório de Tratamento Térmico',                          '', 'laboratorio', '11.01.17.03'),
    ('11.01.17.03.09', 'CT - DEM - Laboratório de Acionamentos e Comandos Hidropneumáticos',    '', 'laboratorio', '11.01.17.03'),
    ('11.01.17.03.10', 'CT - DEM - Laboratório de Materiais e Produtos Cerâmicos',              '', 'laboratorio', '11.01.17.03'),
    ('11.01.17.50',    'CT - DEM - Laboratório de Integridade e Inspeção',                       '', 'laboratorio', '11.01.17.03'),
    ('11.01.17.46',    'CT - DEM - Laboratório de Inovação',                                     '', 'laboratorio', '11.01.17.03'),

    # ── Nível 3: DEQ ─────────────────────────────────────────────────────────
    ('11.00.55.65',    'CT - DEQ - Secretaria do Departamento de Engenharia Química',             '', 'secretaria',  '11.01.17.14'),
    ('11.00.55.19',    'CT - DEQ - Laboratório de Águas, Catálise e Química Ambiental',          '', 'laboratorio', '11.01.17.14'),
    ('11.01.17.14.02', 'CT - DEQ - Laboratório de Análise de Processos Químicos',               '', 'laboratorio', '11.01.17.14'),
    ('11.01.17.14.01', 'CT - DEQ - Laboratório de Análise e Processamento de Dados',            '', 'laboratorio', '11.01.17.14'),
    ('11.01.17.45',    'CT - DEQ - Laboratório de Análises e Pesquisas de Bebidas Alcoólicas',   '', 'laboratorio', '11.01.17.14'),
    ('11.01.17.14.06', 'CT - DEQ - Laboratório de Bioengenharia',                               '', 'laboratorio', '11.01.17.14'),
    ('11.01.17.14.07', 'CT - DEQ - Laboratório de Carvão Ativado',                              '', 'laboratorio', '11.01.17.14'),
    ('11.00.55.03',    'CT - DEQ - Laboratório de Cromatografia e Quimiometria',                 '', 'laboratorio', '11.01.17.14'),
    ('11.01.17.14.08', 'CT - DEQ - Laboratório de Fenômenos de Transporte',                     '', 'laboratorio', '11.01.17.14'),
    ('11.00.55.20',    'CT - DEQ - Laboratório de Fluidodinâmica e Secagem',                    '', 'laboratorio', '11.01.17.14'),
    ('11.00.55.09',    'CT - DEQ - Laboratório de Microbiologia Industrial',                    '', 'laboratorio', '11.01.17.14'),
    ('11.00.55.17',    'CT - DEQ - Laboratório de Modelagem e Simulação de Processos',          '', 'laboratorio', '11.01.17.14'),
    ('11.00.55.15',    'CT - DEQ - Laboratório de Operações Unitárias',                         '', 'laboratorio', '11.01.17.14'),
    ('11.00.55.16',    'CT - DEQ - Laboratório de Petróleo',                                    '', 'laboratorio', '11.01.17.14'),
    ('11.01.17.14.04', 'CT - DEQ - Laboratório de Produtos Fermentos e Destilados',             '', 'laboratorio', '11.01.17.14'),
    ('11.01.17.14.05', 'CT - DEQ - Laboratório de Reatores Químicos',                           '', 'laboratorio', '11.01.17.14'),
    ('11.00.55.18',    'CT - DEQ - Laboratório de Tecnologia Cosmética',                        '', 'laboratorio', '11.01.17.14'),
    ('11.00.55.14',    'CT - DEQ - Laboratório de Tecnologia Química',                          '', 'laboratorio', '11.01.17.14'),
    ('11.01.17.14.09', 'CT - DEQ - Laboratório de Termodinâmica',                              '', 'laboratorio', '11.01.17.14'),
    ('11.01.17.14.03', 'CT - DEQ - Laboratório Piloto de Química',                              '', 'laboratorio', '11.01.17.14'),

    # ── Nível 3: NUPPA ───────────────────────────────────────────────────────
    ('11.01.17.09.01', 'NUPPA - Laboratório de Controle de Qualidade', '', 'laboratorio', '11.01.17.09'),
    ('11.01.17.09.02', 'NUPPA - Laboratório de Microbiologia',         '', 'laboratorio', '11.01.17.09'),

    # ── Nível 3: PPGCTA ──────────────────────────────────────────────────────
    ('11.01.17.36.01', 'CT - PPGCTA - Laboratório de Microbiologia de Alimentos', '', 'laboratorio', '11.01.17.36'),
]


class Command(BaseCommand):
    help = 'Importa hierarquia completa de setores do CT/UFPB (4 níveis)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            default=False,
            help='Apaga todos os setores antes de reimportar (redefine usuários para setor nulo)',
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            if options['limpar']:
                total = Setor.objects.count()
                Setor.objects.all().delete()
                self.stdout.write(self.style.WARNING(
                    f'  {total} setor(es) apagado(s) — usuários ficam sem setor de lotação.'
                ))

            for codigo_antigo, codigo_correto in CODIGOS_RENUMERADOS.items():
                migrar_codigo_antigo(codigo_antigo, codigo_correto)

            # Primeira passagem: criar/atualizar todos sem pai
            setor_map = {}
            for codigo, nome, sigla, tipo, codigo_pai in HIERARQUIA:
                s, criado = Setor.objects.update_or_create(
                    codigo=codigo,
                    defaults={
                        'nome': nome_padronizado(codigo, nome, sigla),
                        'sigla': sigla,
                        'tipo': tipo,
                        'ativo': True,
                        'pai': None,
                    },
                )
                setor_map[codigo] = s
                if criado:
                    self.stdout.write(f'  [+] {tipo:15} {codigo}  {nome[:60]}')

            # Segunda passagem: vincular os pais
            for codigo, nome, sigla, tipo, codigo_pai in HIERARQUIA:
                codigo_pai = normalizar_codigo_pai(codigo_pai)
                if codigo_pai:
                    pai = setor_map.get(codigo_pai)
                    if pai:
                        Setor.objects.filter(codigo=codigo).update(pai=pai)
                    else:
                        self.stdout.write(self.style.WARNING(
                            f'  [!] Pai {codigo_pai} não encontrado para {codigo}'
                        ))

            direcao_correta = setor_map.get(CODIGO_DIRECAO_CORRETO)
            if direcao_correta:
                Setor.objects.filter(pai__codigo=CODIGO_DIRECAO_ANTIGO).update(pai=direcao_correta)
            Setor.objects.filter(codigo=CODIGO_DIRECAO_ANTIGO).update(
                nome='Cadastro incorreto substituído por 11.01.17.01',
                sigla='',
                ativo=False,
            )
            Setor.objects.filter(codigo=CODIGO_GABINETE_ANTIGO).update(
                nome='Cadastro incorreto substituído por 11.01.17.01.13',
                sigla='',
                ativo=False,
            )

        # Contagens finais
        total = Setor.objects.count()
        por_tipo = {}
        for s in Setor.objects.all():
            por_tipo[s.tipo] = por_tipo.get(s.tipo, 0) + 1

        self.stdout.write(self.style.SUCCESS(f'\nTotal de setores: {total}'))
        for tipo, qtd in sorted(por_tipo.items()):
            label = dict(
                centro='Centro', direcao='Direção', administrativo='Administrativos',
                departamento='Departamentos', coordenacao_g='Coord. Graduação',
                coordenacao_pg='Prog. Pós-Grad.', laboratorio='Laboratórios',
                secretaria='Secretarias de Depto',
            ).get(tipo, tipo)
            self.stdout.write(f'  {label:30} {qtd:3}')
