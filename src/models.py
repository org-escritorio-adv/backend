# Importa todos os models para registrá-los no Base.metadata antes do create_all
from src.usuarios.model import Usuario  
from src.clientes.model import Cliente  
from src.processos.model import Processo  
from src.movimentacoes.model import Movimentacao  
from src.tarefas.model import Tarefa  
from src.prazos.model import Prazo  
from src.leads.model import LeadSite
from src.auth.model import PasswordResetToken  
