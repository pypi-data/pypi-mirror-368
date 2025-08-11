import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind
} from 'vscode-languageclient/node';
import * as path from 'path';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    console.log('NovaLang extension is now active!');

    // The server is implemented in Python
    const serverModule = path.join(context.extensionPath, '..', 'language-server', 'novalang_lsp.py');
    
    // If the extension is launched in debug mode then the debug server options are used
    // Otherwise the run options are used
    const serverOptions: ServerOptions = {
        run: { command: 'python', args: [serverModule], transport: TransportKind.stdio },
        debug: { command: 'python', args: [serverModule], transport: TransportKind.stdio }
    };

    // Options to control the language client
    const clientOptions: LanguageClientOptions = {
        // Register the server for NovaLang documents
        documentSelector: [{ scheme: 'file', language: 'novalang' }],
        synchronize: {
            // Notify the server about file changes to '.nova' files contained in the workspace
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.nova')
        }
    };

    // Create the language client and start the client.
    client = new LanguageClient(
        'novalangLanguageServer',
        'NovaLang Language Server',
        serverOptions,
        clientOptions
    );

    // Start the client. This will also launch the server
    client.start();

    // Register commands
    registerCommands(context);

    // Show welcome message
    vscode.window.showInformationMessage('NovaLang extension activated! 🚀');
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

function registerCommands(context: vscode.ExtensionContext) {
    // Run NovaLang file
    const runFileCommand = vscode.commands.registerCommand('novalang.runFile', async () => {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) {
            vscode.window.showErrorMessage('No active NovaLang file');
            return;
        }

        const config = vscode.workspace.getConfiguration('novalang');
        const pythonPath = config.get<string>('pythonPath', 'python');
        const mainScript = config.get<string>('mainScript', 'main.py');
        
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder found');
            return;
        }

        const terminal = vscode.window.createTerminal({
            name: 'NovaLang',
            cwd: workspaceFolder.uri.fsPath
        });

        const filePath = activeEditor.document.fileName;
        terminal.sendText(`${pythonPath} ${mainScript} "${filePath}"`);
        terminal.show();
    });

    // Create Component
    const createComponentCommand = vscode.commands.registerCommand('novalang.createComponent', async (uri) => {
        const componentName = await vscode.window.showInputBox({
            prompt: 'Enter component name',
            placeHolder: 'MyComponent'
        });

        if (componentName) {
            const componentContent = `@Component
class ${componentName} {
    state = {
        // component state
    }
    
    function render(props) {
        return \`
            <div>
                <h1>Hello from ${componentName}!</h1>
            </div>
        \`
    }
    
    function onMount() {
        print "🎯 ${componentName} mounted"
    }
}

export ${componentName}
`;

            const folderUri = uri || vscode.workspace.workspaceFolders?.[0]?.uri;
            if (folderUri) {
                const fileUri = vscode.Uri.joinPath(folderUri, `${componentName}.nova`);
                await vscode.workspace.fs.writeFile(fileUri, Buffer.from(componentContent));
                const document = await vscode.workspace.openTextDocument(fileUri);
                vscode.window.showTextDocument(document);
            }
        }
    });

    // Create Entity
    const createEntityCommand = vscode.commands.registerCommand('novalang.createEntity', async (uri) => {
        const entityName = await vscode.window.showInputBox({
            prompt: 'Enter entity name',
            placeHolder: 'User'
        });

        if (entityName) {
            const entityContent = `@Entity
class ${entityName} {
    id: number
    name: string
    createdAt: string
    
    function ${entityName}(data) {
        this.id = data.id
        this.name = data.name
        this.createdAt = data.createdAt || new Date().toISOString()
    }
    
    function validate() {
        if (!this.name || this.name.length < 2) {
            return "Name must be at least 2 characters"
        }
        return null
    }
    
    function toJSON() {
        return {
            id: this.id,
            name: this.name,
            createdAt: this.createdAt
        }
    }
}

export ${entityName}
`;

            const folderUri = uri || vscode.workspace.workspaceFolders?.[0]?.uri;
            if (folderUri) {
                const fileUri = vscode.Uri.joinPath(folderUri, `${entityName}.nova`);
                await vscode.workspace.fs.writeFile(fileUri, Buffer.from(entityContent));
                const document = await vscode.workspace.openTextDocument(fileUri);
                vscode.window.showTextDocument(document);
            }
        }
    });

    // Create Service
    const createServiceCommand = vscode.commands.registerCommand('novalang.createService', async (uri) => {
        const serviceName = await vscode.window.showInputBox({
            prompt: 'Enter service name',
            placeHolder: 'UserService'
        });

        if (serviceName) {
            const serviceContent = `@Service
class ${serviceName} {
    
    function processData(data) {
        print "⚙️ ${serviceName}.processData()"
        // business logic here
        return data
    }
    
    function validateInput(input) {
        print "✅ ${serviceName}.validateInput()"
        // validation logic
        return input !== null && input !== undefined
    }
    
    function calculateResult(params) {
        print "🧮 ${serviceName}.calculateResult()"
        // calculation logic
        return params.reduce((sum, val) => sum + val, 0)
    }
}

export ${serviceName}
`;

            const folderUri = uri || vscode.workspace.workspaceFolders?.[0]?.uri;
            if (folderUri) {
                const fileUri = vscode.Uri.joinPath(folderUri, `${serviceName}.nova`);
                await vscode.workspace.fs.writeFile(fileUri, Buffer.from(serviceContent));
                const document = await vscode.workspace.openTextDocument(fileUri);
                vscode.window.showTextDocument(document);
            }
        }
    });

    // Create Controller
    const createControllerCommand = vscode.commands.registerCommand('novalang.createController', async (uri) => {
        const controllerName = await vscode.window.showInputBox({
            prompt: 'Enter controller name',
            placeHolder: 'UserController'
        });

        if (controllerName) {
            const endpoint = await vscode.window.showInputBox({
                prompt: 'Enter API endpoint',
                placeHolder: '/api/users'
            });

            const controllerContent = `@Controller("${endpoint || '/api/resource'}")
class ${controllerName} {
    
    function GET index() {
        print "🌐 GET ${endpoint || '/api/resource'}"
        return {
            status: 200,
            data: [
                // your data here
            ]
        }
    }
    
    function POST create(request) {
        print "🌐 POST ${endpoint || '/api/resource'}"
        const data = request.body
        
        // validation
        if (!data.name) {
            return {
                status: 400,
                error: "Name is required"
            }
        }
        
        // create logic here
        return {
            status: 201,
            data: data
        }
    }
    
    function GET show(id) {
        print "🌐 GET ${endpoint || '/api/resource'}/" + id
        return {
            status: 200,
            data: {
                id: id
                // resource data
            }
        }
    }
    
    function PUT update(id, request) {
        print "🌐 PUT ${endpoint || '/api/resource'}/" + id
        return {
            status: 200,
            data: {
                id: id,
                // updated data
            }
        }
    }
    
    function DELETE destroy(id) {
        print "🌐 DELETE ${endpoint || '/api/resource'}/" + id
        return {
            status: 204
        }
    }
}

export ${controllerName}
`;

            const folderUri = uri || vscode.workspace.workspaceFolders?.[0]?.uri;
            if (folderUri) {
                const fileUri = vscode.Uri.joinPath(folderUri, `${controllerName}.nova`);
                await vscode.workspace.fs.writeFile(fileUri, Buffer.from(controllerContent));
                const document = await vscode.workspace.openTextDocument(fileUri);
                vscode.window.showTextDocument(document);
            }
        }
    });

    // Create Project
    const createProjectCommand = vscode.commands.registerCommand('novalang.createProject', async () => {
        const projectName = await vscode.window.showInputBox({
            prompt: 'Enter project name',
            placeHolder: 'my-nova-app'
        });

        if (projectName) {
            const folderUri = await vscode.window.showOpenDialog({
                canSelectFolders: true,
                canSelectFiles: false,
                canSelectMany: false,
                openLabel: 'Select Project Location'
            });

            if (folderUri && folderUri[0]) {
                const projectUri = vscode.Uri.joinPath(folderUri[0], projectName);
                
                // Create project structure
                await vscode.workspace.fs.createDirectory(projectUri);
                await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(projectUri, 'src'));
                await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(projectUri, 'src', 'components'));
                await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(projectUri, 'src', 'entities'));
                await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(projectUri, 'src', 'services'));
                await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(projectUri, 'src', 'controllers'));

                // Create main application file
                const appContent = `@Application
class ${projectName.replace(/[-_]/g, '')}App {
    
    function start() {
        print "🚀 Starting ${projectName}..."
        // Application initialization
    }
    
    function configure() {
        print "⚙️ Configuring application..."
        // Configuration setup
    }
}

const app = new ${projectName.replace(/[-_]/g, '')}App()
app.configure()
app.start()
`;

                await vscode.workspace.fs.writeFile(
                    vscode.Uri.joinPath(projectUri, 'app.nova'),
                    Buffer.from(appContent)
                );

                // Create README
                const readmeContent = `# ${projectName}

A NovaLang full-stack application.

## Project Structure

- \`src/components/\` - Frontend components
- \`src/entities/\` - Shared data models
- \`src/services/\` - Business logic
- \`src/controllers/\` - API endpoints

## Getting Started

1. Open the project in VS Code
2. Run \`app.nova\` with F5
3. Start building your application!

## Commands

- **Create Component**: Ctrl+Alt+C
- **Run File**: F5
- Right-click in explorer for more options

---

Built with ❤️ using NovaLang
`;

                await vscode.workspace.fs.writeFile(
                    vscode.Uri.joinPath(projectUri, 'README.md'),
                    Buffer.from(readmeContent)
                );

                // Open the new project
                await vscode.commands.executeCommand('vscode.openFolder', projectUri);
            }
        }
    });

    // Register all commands
    context.subscriptions.push(
        runFileCommand,
        createComponentCommand,
        createEntityCommand,
        createServiceCommand,
        createControllerCommand,
        createProjectCommand
    );
}
