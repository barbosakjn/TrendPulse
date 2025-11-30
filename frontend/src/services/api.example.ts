/**
 * EXEMPLO DE USO DO SERVIÇO DE API
 * Este arquivo mostra como usar o apiClient em seus componentes
 */

import { apiClient } from './api';

// ============================================================================
// EXEMPLOS DE AUTENTICAÇÃO
// ============================================================================

/**
 * Exemplo 1: Registrar novo usuário
 */
async function exemploRegistro() {
  try {
    const result = await apiClient.register({
      email: 'usuario@example.com',
      password: 'SenhaForte123',
      name: 'Nome do Usuário',
      preferred_language: 'pt_BR',
    });

    console.log('Usuário registrado:', result.user);
    console.log('Mensagem:', result.message);
  } catch (error) {
    console.error('Erro no registro:', error);
  }
}

/**
 * Exemplo 2: Fazer login
 */
async function exemploLogin() {
  try {
    const response = await apiClient.login({
      email: 'usuario@example.com',
      password: 'SenhaForte123',
      remember_me: true,
    });

    console.log('Login bem-sucedido!');
    console.log('Access Token:', response.access_token);
    console.log('Refresh Token:', response.refresh_token);
    console.log('Usuário:', response.user);

    // Os tokens já foram armazenados automaticamente!
  } catch (error) {
    console.error('Erro no login:', error);
  }
}

/**
 * Exemplo 3: Fazer logout
 */
async function exemploLogout() {
  try {
    await apiClient.logout();
    console.log('Logout realizado com sucesso!');
    // Usuário será redirecionado para /login automaticamente
  } catch (error) {
    console.error('Erro no logout:', error);
  }
}

/**
 * Exemplo 4: Obter perfil do usuário atual
 */
async function exemploObterPerfil() {
  try {
    const user = await apiClient.getCurrentUser();
    console.log('Perfil do usuário:', user);
  } catch (error) {
    console.error('Erro ao obter perfil:', error);
  }
}

/**
 * Exemplo 5: Solicitar reset de senha
 */
async function exemploResetSenha() {
  try {
    const result = await apiClient.requestPasswordReset('usuario@example.com');
    console.log(result.message);
  } catch (error) {
    console.error('Erro ao solicitar reset:', error);
  }
}

// ============================================================================
// EXEMPLOS DE REQUISIÇÕES GENÉRICAS
// ============================================================================

/**
 * Exemplo 6: GET request com autenticação automática
 */
async function exemploGet() {
  try {
    // O header Authorization é adicionado automaticamente!
    const trends = await apiClient.get('/api/trends');
    console.log('Trends:', trends);
  } catch (error) {
    console.error('Erro ao buscar trends:', error);
  }
}

/**
 * Exemplo 7: POST request com autenticação automática
 */
async function exemploPost() {
  try {
    const newTrend = await apiClient.post('/api/trends', {
      keyword: 'AI Tools',
      category: 'technology',
    });
    console.log('Trend criado:', newTrend);
  } catch (error) {
    console.error('Erro ao criar trend:', error);
  }
}

/**
 * Exemplo 8: PUT request
 */
async function exemploPut() {
  try {
    const updated = await apiClient.put('/api/trends/123', {
      keyword: 'AI Tools Updated',
    });
    console.log('Trend atualizado:', updated);
  } catch (error) {
    console.error('Erro ao atualizar:', error);
  }
}

/**
 * Exemplo 9: DELETE request
 */
async function exemploDelete() {
  try {
    await apiClient.delete('/api/trends/123');
    console.log('Trend deletado com sucesso!');
  } catch (error) {
    console.error('Erro ao deletar:', error);
  }
}

// ============================================================================
// EXEMPLOS DE USO EM COMPONENTES REACT
// ============================================================================

/**
 * Exemplo 10: Usar em um componente React
 */
/*
import { useState } from 'react';
import { apiClient } from '@/services/api';

function LoginComponent() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await apiClient.login({ email, password });
      console.log('Login bem-sucedido:', response.user);
      // Redirecionar para dashboard
      window.location.href = '/dashboard';
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Senha"
      />
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? 'Entrando...' : 'Entrar'}
      </button>
    </form>
  );
}
*/

/**
 * Exemplo 11: Verificar se usuário está autenticado
 */
function exemploVerificarAutenticacao() {
  const isAuth = apiClient.isAuthenticated();
  console.log('Usuário autenticado?', isAuth);

  const user = apiClient.getStoredUser();
  console.log('Usuário armazenado:', user);
}

/**
 * Exemplo 12: Proteção de rotas
 */
/*
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/services/api';

function ProtectedPage() {
  const router = useRouter();

  useEffect(() => {
    if (!apiClient.isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  return <div>Conteúdo protegido</div>;
}
*/

// ============================================================================
// RECURSOS AUTOMÁTICOS DO SERVIÇO
// ============================================================================

/**
 * O serviço apiClient faz automaticamente:
 *
 * ✅ 1. POST para http://localhost:8000/api/auth/register
 * ✅ 2. POST para http://localhost:8000/api/auth/login
 * ✅ 3. Armazena tokens (access_token e refresh_token) no localStorage
 * ✅ 4. Intercepta requests para adicionar Authorization header
 * ✅ 5. Trata erro de token expirado (401):
 *    - Tenta renovar o token automaticamente
 *    - Reenvia a requisição original com novo token
 *    - Se falhar, faz logout e redireciona para /login
 *
 * FUNCIONALIDADES EXTRAS:
 * ✅ Fila de requisições durante refresh de token
 * ✅ Métodos genéricos (get, post, put, delete)
 * ✅ Tratamento de erros padronizado
 * ✅ TypeScript com tipos completos
 * ✅ Singleton pattern (uma única instância)
 * ✅ SSR-safe (verifica se está no browser)
 */

export {};
