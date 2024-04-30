local telescope = require("telescope.builtin")
vim.g.mapleader = " "
vim.keymap.set("n", "<leader>pv", vim.cmd.Ex)
vim.keymap.set("n", "<leader>pf", telescope.find_files, {})
vim.keymap.set("n", "<C-p>", telescope.git_files, {})
vim.keymap.set("n", "<leader>ps", function()
    telescope.grep_string({ search = vim.fn.input("Grep > ")})
end)
