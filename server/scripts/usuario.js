#!/usr/bin/env node
// Gestión de usuarios desde la terminal, por si hace falta sin abrir la app:
//   npm run usuario -- agregar juan MiClaveSegura1
//   npm run usuario -- listar
//   npm run usuario -- quitar juan
import { addUser, removeUser, listUsers } from '../auth.js';

const [accion, nombre, password] = process.argv.slice(2);

try {
  switch (accion) {
    case 'agregar':
      console.log(`✓ Usuario "${await addUser(nombre, password)}" creado.`);
      break;
    case 'quitar':
      removeUser(nombre);
      console.log(`✓ Usuario "${nombre}" eliminado.`);
      break;
    case 'listar': {
      const us = listUsers();
      console.log(us.length ? us.map((u) => `• ${u}`).join('\n') : 'No hay usuarios.');
      break;
    }
    default:
      console.log(
        'Uso:\n' +
          '  npm run usuario -- agregar <usuario> <contraseña>\n' +
          '  npm run usuario -- quitar  <usuario>\n' +
          '  npm run usuario -- listar',
      );
  }
} catch (err) {
  console.error(`✗ ${err.message}`);
  process.exit(1);
}
