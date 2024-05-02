local nvim_tree = require("nvim-tree")

nvim_tree.setup({
    filters = {
        dotfiles = false,
    },
    git = {
        enable = true,
        ignore = false,
        timeout = 500,
    }
})
