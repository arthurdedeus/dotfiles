local lsp = require('lsp-zero').preset({})
local navic = require('nvim-navic')

lsp.on_attach(function(client, bufnr)
    lsp.default_keymaps({buffer = bufnr})
    if client.server_capabilities.documentSymbolProvider then
        navic.attach(client, bufnr)
    end
end)

require("mason").setup({
        ui = {
        icons = {
            package_installed = "✓",
            package_pending = "➜",
            package_uninstalled = "✗"
        }
    }
})

require('mason-lspconfig').setup({
  ensure_installed = {
      "lua_ls",
      "docker_compose_language_server",
      "dockerls",
      "html",
      "jsonls",
      "pyright",
      "ruff",
      "tsserver",
  },
  handlers = {
    function(server_name)
      require('lspconfig')[server_name].setup({})
    end,

    pyright = function()
        require("lspconfig").pyright.setup({})
    end,

    lua_ls = function()
        require("lspconfig").lua_ls.setup({
              settings = {
                  Lua = {
                      diagnostics = {
                          globals = {'vim'}
                      }
                  }
              }
          })
    end,
  },

})

lsp.setup()

