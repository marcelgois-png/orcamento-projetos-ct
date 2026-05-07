"""
Comando para carregar os setores do Centro de Tecnologia da UFPB
conforme a hierarquia organizacional do SIPAC.

Uso: python manage.py load_setores
     python manage.py load_setores --limpar   (apaga setores existentes antes)
"""
from django.core.management.base import BaseCommand
from core.models import Setor

CODIGO_DIRECAO = '11.01.17.01'
CODIGO_CT = '11.00.55'

TIPOS_POR_CODIGO = {
    CODIGO_CT: 'centro',
    CODIGO_DIRECAO: 'direcao',
}


def normalizar_codigo_pai(codigo, codigo_pai):
    if codigo_pai == CODIGO_CT and codigo not in (CODIGO_CT, CODIGO_DIRECAO):
        return CODIGO_DIRECAO
    return codigo_pai


def inferir_tipo(codigo, nome, codigo_pai):
    if codigo in TIPOS_POR_CODIGO:
        return TIPOS_POR_CODIGO[codigo]

    nome_lower = str(nome).lower()
    if 'secretaria do departamento' in nome_lower:
        return 'secretaria'
    if 'departamento' in nome_lower or 'núcleo de pesquisa' in nome_lower:
        return 'departamento'
    if 'coordenação' in nome_lower or 'coordena' in nome_lower:
        return 'coordenacao_g'
    if 'pós-graduação' in nome_lower or 'pos-graduacao' in nome_lower:
        return 'coordenacao_pg'
    if normalizar_codigo_pai(codigo, codigo_pai) == CODIGO_DIRECAO and any(
        termo in nome_lower
        for termo in ('arquivo', 'assessoria', 'biblioteca', 'comissão', 'gabinete', 'setor ', 'almoxarifado')
    ):
        return 'administrativo'
    return 'laboratorio'


def nome_padronizado(codigo, nome, sigla):
    if codigo == CODIGO_CT:
        return 'CT - Centro de Tecnologia'
    if codigo == CODIGO_DIRECAO:
        return 'CT - DIREÇÃO DE CENTRO'

    base = ' '.join(str(nome).split())
    if base.startswith('CT - '):
        base = base[5:].strip()
    if sigla and base.startswith(f'{sigla} - '):
        base = base[len(sigla) + 3:].strip()

    return f'CT - {sigla} - {base}' if sigla else f'CT - {base}'

# Formato: (codigo, nome, sigla, codigo_pai)
SETORES = [
    # ── Raiz ─────────────────────────────────────────────────────────────
    ('11.00.55', 'Centro de Tecnologia', 'CT', None),

    # ── Direto sob o CT (sem departamento) ───────────────────────────────
    ('11.00.55.01', 'Programa de Pós-Graduação em Engenharia Química', '', '11.00.55'),
    ('11.00.55.51', 'Arquivo', '', '11.00.55'),
    ('11.00.55.55', 'Programa de Pós-Graduação em Engenharia de Produção e Sistemas', '', '11.00.55'),
    ('11.00.55.56', 'Curso de Especialização em Assistência Técnica nas Áreas de Arquitetura, Urbanismo e Engenharia', '', '11.00.55'),
    ('11.00.55.57', 'Laboratório de Análises Computacionais em Meio Ambiente', '', '11.00.55'),

    # ── Direção de Centro ─────────────────────────────────────────────────
    ('11.01.17.01', 'CT - DIREÇÃO DE CENTRO', 'CT-DC', '11.00.55'),
    ('11.00.55.02', 'Setor de Portaria', '', '11.01.17.01'),
    ('11.00.55.13', 'Assessoria de Extensão', '', '11.01.17.01'),
    ('11.00.55.50', 'Secretaria', '', '11.01.17.01'),
    ('11.00.55.58', 'Comissão Interna de Biossegurança', '', '11.01.17.01'),
    ('11.00.55.66', 'Comissão Permanente de Sindicância', '', '11.01.17.01'),
    ('11.01.17.01.07', 'Laboratório de Informática Gráfica', '', '11.01.17.01'),
    ('11.01.17.01.08', 'Almoxarifado', '', '11.01.17.01'),
    ('11.01.17.01.09', 'Assessoria de Administração', '', '11.01.17.01'),
    ('11.01.17.01.10', 'Assessoria de Graduação', '', '11.01.17.01'),
    ('11.01.17.01.11', 'Assessoria de Planejamento', '', '11.01.17.01'),
    ('11.01.17.01.12', 'Setor de Gestão de Pessoas', '', '11.01.17.01'),
    ('11.01.17.01.13', 'Gabinete da Direção do CT', 'GDC', '11.01.17.01'),

    # ── DEM — Departamento de Engenharia Mecânica ─────────────────────────
    ('11.01.17.03', 'Departamento de Engenharia Mecânica', 'DEM', '11.00.55'),
    ('11.00.55.04', 'Laboratório de Carvão Ativado', '', '11.01.17.03'),
    ('11.00.55.06', 'Laboratório de Inovação e Conversão Térmica', '', '11.01.17.03'),
    ('11.00.55.08', 'Laboratório de Automação e Controle', '', '11.01.17.03'),
    ('11.00.55.11', 'Laboratório de Energia Sustentável', '', '11.01.17.03'),
    ('11.00.55.12', 'Laboratório de Conformação Mecânica', '', '11.01.17.03'),
    ('11.00.55.27', 'Laboratório de Controle de Vibração e Ruído', '', '11.01.17.03'),
    ('11.00.55.28', 'Laboratório de Dinâmica', '', '11.01.17.03'),
    ('11.00.55.29', 'Laboratório de Instrumentação e Controle', '', '11.01.17.03'),
    ('11.00.55.31', 'Laboratório de Engenharia de Precisão', '', '11.01.17.03'),
    ('11.00.55.32', 'Laboratório de Ensaios Mecânicos', '', '11.01.17.03'),
    ('11.00.55.34', 'Laboratório de Mecatrônica', '', '11.01.17.03'),
    ('11.00.55.35', 'Laboratório de Metalografia', '', '11.01.17.03'),
    ('11.00.55.36', 'Laboratório de Metrologia Dimensional', '', '11.01.17.03'),
    ('11.00.55.44', 'Laboratório de Representação Gráfica', '', '11.01.17.03'),
    ('11.00.55.49', 'Laboratório de Transferência de Calor e Massa', '', '11.01.17.03'),
    ('11.00.55.53', 'Laboratório de Atividades Meteorológicas', '', '11.01.17.03'),
    ('11.00.55.62', 'Secretaria do Departamento de Engenharia Mecânica', '', '11.01.17.03'),
    ('11.01.17.50', 'Laboratório de Integridade e Inspeção', '', '11.01.17.03'),
    ('11.01.17.03.03', 'Laboratório de Máquinas e Acionamentos Elétricos', '', '11.01.17.03'),
    ('11.01.17.03.04', 'Laboratório de Motores de Combustão Interna', '', '11.01.17.03'),
    ('11.01.17.03.05', 'Laboratório de Oficina Mecânica', '', '11.01.17.03'),
    ('11.01.17.03.06', 'Laboratório de Refrigeração e Ar Condicionado', '', '11.01.17.03'),
    ('11.01.17.03.07', 'Laboratório de Solidificação Rápida', '', '11.01.17.03'),
    ('11.01.17.03.08', 'Laboratório de Tratamento Térmico', '', '11.01.17.03'),
    ('11.01.17.03.09', 'Laboratório de Acionamentos e Comandos Hidropneumáticos', '', '11.01.17.03'),
    ('11.01.17.03.10', 'Laboratório de Materiais e Produtos Cerâmicos', '', '11.01.17.03'),

    # ── DAU — Departamento de Arquitetura e Urbanismo ──────────────────────
    ('11.01.17.05', 'Departamento de Arquitetura e Urbanismo', 'DAU', '11.00.55'),
    ('11.00.55.22', 'Laboratório de Modelos e Prototipagem', '', '11.01.17.05'),
    ('11.00.55.23', 'Laboratório de Ambiente Urbano e Edificado', '', '11.01.17.05'),
    ('11.00.55.26', 'Laboratório de Conforto Ambiental', '', '11.01.17.05'),
    ('11.00.55.33', 'Laboratório de Estudos sobre Cidade, Cultura e Urbanidade', '', '11.01.17.05'),
    ('11.00.55.60', 'Secretaria do Departamento de Arquitetura e Urbanismo', '', '11.01.17.05'),
    ('11.01.17.05.01', 'Laboratório de Pesquisa, Projeto e Memória', '', '11.01.17.05'),
    ('11.01.17.05.02', 'Laboratório de Acessibilidade (LACESSE)', '', '11.01.17.05'),

    # ── DEP — Departamento de Engenharia de Produção ──────────────────────
    ('11.01.17.06', 'Departamento de Engenharia de Produção', 'DEP', '11.00.55'),
    ('11.00.55.25', 'Laboratório de Análise do Trabalho', '', '11.01.17.06'),
    ('11.00.55.64', 'Secretaria do Departamento de Engenharia de Produção', '', '11.01.17.06'),
    ('11.01.17.06.01', 'Laboratório de Métodos Quantitativos Aplicados', '', '11.01.17.06'),
    ('11.01.17.06.02', 'Laboratório de Desenvolvimento de Produtos e Inovação', '', '11.01.17.06'),
    ('11.01.17.06.03', 'Laboratório de Engenharia de Sustentabilidade e Consumo', '', '11.01.17.06'),
    ('11.01.17.06.04', 'Laboratório de Simulação de Processo Discreto', '', '11.01.17.06'),
    ('11.01.17.06.05', 'Laboratório de Informática — DEP', '', '11.01.17.06'),

    # ── NUPPA ─────────────────────────────────────────────────────────────
    ('11.01.17.09', 'Núcleo de Pesquisa e Processamento de Alimentos (NUPPA)', 'NUPPA', '11.00.55'),
    ('11.01.17.09.01', 'Laboratório de Controle de Qualidade — NUPPA', '', '11.01.17.09'),
    ('11.01.17.09.02', 'Laboratório de Microbiologia — NUPPA', '', '11.01.17.09'),
    ('11.01.17.09.03', 'Laboratório de Físico-Química — NUPPA', '', '11.01.17.09'),

    # ── Laboratório de Energia Solar ─────────────────────────────────────
    ('11.01.17.10', 'Laboratório de Energia Solar', '', '11.00.55'),

    # ── DECA — Departamento de Engenharia Civil e Ambiental ───────────────
    ('11.01.17.13', 'Departamento de Engenharia Civil e Ambiental', 'DECA', '11.00.55'),
    ('11.00.55.24', 'Laboratório de Análise Estrutural e Avaliação de Desempenho', '', '11.01.17.13'),
    ('11.00.55.37', 'Laboratório de Pesquisa em Sistemas Ambientais Urbanos', '', '11.01.17.13'),
    ('11.00.55.42', 'Laboratório de Química Ambiental', '', '11.01.17.13'),
    ('11.00.55.43', 'Laboratório de Reologia', '', '11.01.17.13'),
    ('11.00.55.46', 'Laboratório de Modelos Físicos Qualitativos e Computacionais', '', '11.01.17.13'),
    ('11.00.55.48', 'Laboratório de Planejamento de Transportes', '', '11.01.17.13'),
    ('11.00.55.54', 'Laboratório de Modelagem da Informação da Construção e Modelagem e Experimentação de Estruturas', '', '11.01.17.13'),
    ('11.00.55.59', 'Secretaria do Departamento de Engenharia Civil e Ambiental', '', '11.01.17.13'),
    ('11.01.17.13.01', 'Laboratório de Recursos Hídricos e Engenharia Ambiental', '', '11.01.17.13'),
    ('11.01.17.13.02', 'Laboratório de Eficiência Energética e Hidráulica em Saneamento (LEHNS)', '', '11.01.17.13'),
    ('11.01.17.13.03', 'Laboratório de Hidráulica', '', '11.01.17.13'),
    ('11.01.17.13.04', 'Laboratório de Geotecnia e Pavimentação', '', '11.01.17.13'),
    ('11.01.17.13.05', 'Laboratório de Topografia', '', '11.01.17.13'),
    ('11.01.17.13.06', 'Laboratório de Saneamento Ambiental', '', '11.01.17.13'),
    ('11.01.17.13.07', 'Laboratório de Ensaios de Materiais e Estruturas (LABEME)', '', '11.01.17.13'),

    # ── DEQ — Departamento de Engenharia Química ──────────────────────────
    ('11.01.17.14', 'Departamento de Engenharia Química', 'DEQ', '11.00.55'),
    ('11.00.55.03', 'Laboratório de Cromatografia e Quimiometria', '', '11.01.17.14'),
    ('11.00.55.09', 'Laboratório de Microbiologia Industrial', '', '11.01.17.14'),
    ('11.00.55.14', 'Laboratório de Tecnologia Química', '', '11.01.17.14'),
    ('11.00.55.15', 'Laboratório de Operações Unitárias', '', '11.01.17.14'),
    ('11.00.55.16', 'Laboratório de Petróleo', '', '11.01.17.14'),
    ('11.00.55.17', 'Laboratório de Modelagem e Simulação de Processos', '', '11.01.17.14'),
    ('11.00.55.18', 'Laboratório de Tecnologia Cosmética', '', '11.01.17.14'),
    ('11.00.55.19', 'Laboratório de Águas, Catálise e Química Ambiental', '', '11.01.17.14'),
    ('11.00.55.20', 'Laboratório de Fluidodinâmica e Secagem', '', '11.01.17.14'),
    ('11.00.55.65', 'Secretaria do Departamento de Engenharia Química', '', '11.01.17.14'),
    ('11.01.17.45', 'Laboratório de Análises e Pesquisas de Bebidas Alcoólicas', '', '11.01.17.14'),
    ('11.01.17.14.01', 'Laboratório de Análise e Processamento de Dados', '', '11.01.17.14'),
    ('11.01.17.14.02', 'Laboratório de Análise de Processos Químicos', '', '11.01.17.14'),
    ('11.01.17.14.03', 'Laboratório Piloto de Química', '', '11.01.17.14'),
    ('11.01.17.14.04', 'Laboratório de Produtos Fermentos e Destilados', '', '11.01.17.14'),
    ('11.01.17.14.05', 'Laboratório de Reatores Químicos', '', '11.01.17.14'),
    ('11.01.17.14.06', 'Laboratório de Bioengenharia', '', '11.01.17.14'),
    ('11.01.17.14.07', 'Laboratório de Carvão Ativado — DEQ', '', '11.01.17.14'),
    ('11.01.17.14.08', 'Laboratório de Fenômenos de Transporte', '', '11.01.17.14'),
    ('11.01.17.14.09', 'Laboratório de Termodinâmica', '', '11.01.17.14'),

    # ── DEA — Departamento de Engenharia de Alimentos ─────────────────────
    ('11.01.17.15', 'Departamento de Engenharia de Alimentos', 'DEA', '11.00.55'),
    ('11.00.55.10', 'Laboratório de Flavor', '', '11.01.17.15'),
    ('11.00.55.21', 'Laboratório de Apoio', '', '11.01.17.15'),
    ('11.00.55.30', 'Laboratório de Extração', '', '11.01.17.15'),
    ('11.00.55.45', 'Laboratório de Processos Microbianos em Alimentos', '', '11.01.17.15'),
    ('11.00.55.61', 'Secretaria do Departamento de Engenharia de Alimentos', '', '11.01.17.15'),
    ('11.00.55.67', 'Laboratório de Engenharia Bioquímica', '', '11.01.17.15'),
    ('11.00.55.68', 'Laboratório de Controle de Qualidade — DEA', '', '11.01.17.15'),
    ('11.01.17.32', 'Laboratório de Análises Químicas de Alimentos', '', '11.01.17.15'),
    ('11.01.17.15.02', 'Laboratório de Bioquímica de Alimentos', '', '11.01.17.15'),
    ('11.01.17.15.03', 'Laboratório de Engenharia de Alimentos', '', '11.01.17.15'),
    ('11.01.17.15.05', 'Laboratório de Tecnologia de Alimentos', '', '11.01.17.15'),
    ('11.01.17.15.06', 'Laboratório de Processamento de Derivados de Pescado', '', '11.01.17.15'),
    ('11.01.17.15.07', 'Laboratório de Análise Sensorial e Desenvolvimento de Novos Produtos', '', '11.01.17.15'),
    ('11.01.17.15.08', 'Laboratório de Processamento de Derivados do Leite', '', '11.01.17.15'),
    ('11.01.17.15.09', 'Laboratório de Tecnologia de Panificação (Padaria Piloto)', '', '11.01.17.15'),
    ('11.01.17.15.10', 'Laboratório de Informática — DEA', '', '11.01.17.15'),
    ('11.01.17.15.11', 'Laboratório de Análises de Ácidos Graxos', '', '11.01.17.15'),
    ('11.01.17.15.12', 'Laboratório de Processamento de Derivados de Carnes', '', '11.01.17.15'),

    # ── DEMAT — Departamento de Engenharia de Materiais ───────────────────
    ('11.01.17.44', 'Departamento de Engenharia de Materiais', 'DEMAT', '11.00.55'),
    ('11.00.55.05', 'Laboratório de Materiais e Biossistemas', '', '11.01.17.44'),
    ('11.00.55.07', 'Laboratório de Materiais Metálicos', '', '11.01.17.44'),
    ('11.00.55.38', 'Laboratório de Purificação e Aspersão de Minerais Argilosos', '', '11.01.17.44'),
    ('11.00.55.39', 'Laboratório de Propriedades Mecânicas dos Materiais', '', '11.01.17.44'),
    ('11.00.55.40', 'Laboratório de Química dos Materiais', '', '11.01.17.44'),
    ('11.00.55.41', 'Laboratório de Materiais Avançados', '', '11.01.17.44'),
    ('11.00.55.47', 'Laboratório de Solidificação Rápida — DEMAT', '', '11.01.17.44'),
    ('11.00.55.63', 'Secretaria do Departamento de Engenharia de Materiais', '', '11.01.17.44'),
    ('11.01.17.44.01', 'Laboratório de Siderurgia', '', '11.01.17.44'),
    ('11.01.17.44.02', 'Laboratório de Cristalografia', '', '11.01.17.44'),
    ('11.01.17.44.03', 'Laboratório de Modelagem de Materiais', '', '11.01.17.44'),
    ('11.01.17.44.04', 'Laboratório de Materiais Poliméricos', '', '11.01.17.44'),
    ('11.01.17.44.05', 'Laboratório de Materiais Cerâmicos', '', '11.01.17.44'),
    ('11.01.17.44.06', 'Laboratório de Caracterização Microestrutural', '', '11.01.17.44'),

    # ── Coordenações ──────────────────────────────────────────────────────
    ('11.01.17.17', 'Coordenação de Engenharia Civil', '', '11.00.55'),
    ('11.01.17.22', 'Biblioteca Setorial', '', '11.00.55'),
    ('11.01.17.23', 'Coordenação de Arquitetura e Urbanismo', '', '11.00.55'),
    ('11.01.17.24', 'Coordenação de Engenharia Ambiental', '', '11.00.55'),
    ('11.01.17.25', 'Coordenação de Engenharia de Alimentos', '', '11.00.55'),
    ('11.01.17.26', 'Coordenação de Engenharia de Materiais', '', '11.00.55'),
    ('11.01.17.27', 'Coordenação de Engenharia de Produção', '', '11.00.55'),
    ('11.01.17.41', 'Coordenação de Engenharia Mecânica', '', '11.00.55'),
    ('11.01.17.42', 'Coordenação de Engenharia Química', '', '11.00.55'),
    ('11.01.17.43', 'Coordenação do Curso de Química Industrial', '', '11.00.55'),
    ('11.01.17.52', 'Coordenação de Engenharia de Produção Mecânica', '', '11.00.55'),

    # ── Programas de Pós-Graduação ────────────────────────────────────────
    ('11.01.17.33', 'Programa de Pós-Graduação em Engenharia Civil e Ambiental', '', '11.00.55'),
    ('11.01.17.34', 'Programa de Pós-Graduação em Arquitetura e Urbanismo', '', '11.00.55'),
    ('11.01.17.35', 'Programa de Pós-Graduação em Ciência e Engenharia de Materiais (PPCEM)', 'PPCEM', '11.00.55'),
    ('11.01.17.36', 'Programa de Pós-Graduação em Ciência e Tecnologia de Alimentos (PPGCTA)', 'PPGCTA', '11.00.55'),
    ('11.01.17.36.01', 'Laboratório de Microbiologia de Alimentos — PPGCTA', '', '11.01.17.36'),
    ('11.01.17.37', 'Programa de Pós-Graduação em Engenharia de Produção', '', '11.00.55'),
    ('11.01.17.39', 'Programa de Pós-Graduação em Engenharia Mecânica', '', '11.00.55'),
    ('11.01.17.40', 'Programa de Pós-Graduação em Engenharia Urbana e Ambiental', '', '11.00.55'),

    # ── Outros ───────────────────────────────────────────────────────────
    ('11.01.17.46', 'Laboratório de Inovação', '', '11.00.55'),
    ('11.01.17.49', 'Programa CT Empreendedor', '', '11.00.55'),
]


class Command(BaseCommand):
    help = 'Carrega os setores do CT-UFPB a partir da lista do SIPAC'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Apaga todos os setores existentes antes de importar'
        )

    def handle(self, *args, **options):
        if options['limpar']:
            count = Setor.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'{count} setores removidos.'))

        criados = 0
        atualizados = 0

        # Primeira passagem: cria todos sem pai
        codigos_criados = {}
        for codigo, nome, sigla, _ in SETORES:
            setor, created = Setor.objects.update_or_create(
                codigo=codigo,
                defaults={
                    'nome': nome_padronizado(codigo, nome, sigla),
                    'sigla': sigla,
                    'tipo': inferir_tipo(codigo, nome, _),
                    'ativo': True,
                }
            )
            codigos_criados[codigo] = setor
            if created:
                criados += 1
            else:
                atualizados += 1

        # Segunda passagem: define hierarquia
        for codigo, nome, sigla, codigo_pai in SETORES:
            codigo_pai = normalizar_codigo_pai(codigo, codigo_pai)
            if codigo_pai:
                pai = codigos_criados.get(codigo_pai)
                if pai:
                    Setor.objects.filter(codigo=codigo).update(pai=pai)
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Pai não encontrado para {codigo}: {codigo_pai}')
                    )

        self.stdout.write(self.style.SUCCESS(
            f'Concluído: {criados} setores criados, {atualizados} atualizados.'
        ))
