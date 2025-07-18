<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const canvasRef = ref(null)
const cols = ref(null)
const rows = ref(null)

const cellSize = 60
let gridData = []

function drawRoundedRect(ctx, x, y, width, height, radius) {
    ctx.beginPath()
    ctx.moveTo(x + radius, y)
    ctx.lineTo(x + width - radius, y)
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
    ctx.lineTo(x + width, y + height - radius)
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height)
    ctx.lineTo(x + radius, y + height)
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius)
    ctx.lineTo(x, y + radius)
    ctx.quadraticCurveTo(x, y, x + radius, y)
    ctx.closePath()
    ctx.fill()
}

function drawCurveBetweenRects(ctx, x1, y1, x2, y2) {
    const halfCell = cellSize / 2
    ctx.beginPath()
    if (x1 == x2) {
        ctx.moveTo(x1, y1 + halfCell)
        ctx.lineTo(x1, y2 + halfCell)
        ctx.lineTo(x1 + cellSize, y2 + halfCell)
        ctx.lineTo(x1 + cellSize, y1 + halfCell)
    } else if (x1 > x2) {
        ctx.moveTo(x1, y1 + halfCell)
        ctx.quadraticCurveTo(x1, y2, x2 + halfCell, y2)
        ctx.lineTo(x1, y2 + halfCell)
        ctx.quadraticCurveTo(x1, y2, x1 + halfCell, y2)
    } else if (y1 === y2) {
        ctx.moveTo(x1 + halfCell, y1)
        ctx.lineTo(x2 + halfCell, y1)
        ctx.lineTo(x2 + halfCell, y1 + cellSize)
        ctx.lineTo(x1 + halfCell, y1 + cellSize)
    } else {
        ctx.moveTo(x1 + cellSize, y1 + halfCell)
        ctx.quadraticCurveTo(x2, y2, x2 + halfCell, y2)
        ctx.lineTo(x2, y2 + halfCell)
        ctx.quadraticCurveTo(x2, y2, x1 + halfCell, y2)
    }
    ctx.closePath()
    ctx.fill()
}

function drawGrid(ctx, canvas) {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    for (let row = 0; row < rows.value; row++) {
        for (let col = 0; col < cols.value; col++) {
            if (gridData[row][col]) {
                const x = col * cellSize
                const y = row * cellSize
                drawRoundedRect(ctx, x, y, cellSize, cellSize, 20)
                if (row + 1 < rows.value && gridData[row + 1][col]) {
                    drawCurveBetweenRects(ctx, x, y, x, y + cellSize)
                }
                if (row + 1 < rows.value && col > 0 && gridData[row + 1][col - 1]) {
                    drawCurveBetweenRects(ctx, x, y, x - cellSize, y + cellSize)
                }
                if (col + 1 < cols.value && gridData[row][col + 1]) {
                    drawCurveBetweenRects(ctx, x, y, x + cellSize, y)
                }
                if (row + 1 < rows.value && col + 1 < cols.value && gridData[row + 1][col + 1]) {
                    drawCurveBetweenRects(ctx, x, y, x + cellSize, y + cellSize)
                }
            }
        }
    }
}

function handleMouseMove(event) {
    const canvas = canvasRef.value
    const rect = canvas.getBoundingClientRect()
    const mouseX = event.clientX - rect.left
    const mouseY = event.clientY - rect.top
    
    const col = Math.floor(mouseX / cellSize)
    const row = Math.floor(mouseY / cellSize)
  
    if (row >= 0 && row < gridData.length && col >= 0 && col < gridData[0].length) {
        if (!gridData[row][col]) {
            gridData[row][col] = true
            const ctx = canvas.getContext('2d')
            drawGrid(ctx, canvas)
            const randomDelay = Math.random() * (10000 - 3000) + 3000
            setTimeout(() => {
                if (gridData[row] && typeof gridData[row][col] !== 'undefined') {
                    gridData[row][col] = false
                    drawGrid(ctx, canvas)
                }
            }, randomDelay)
        }
    }
}

function initCanvas() {
    const rootElement = document.documentElement
    const computedStyles = getComputedStyle(rootElement)
    const cssColor = computedStyles.getPropertyValue('--color-cavas').trim()
    const canvas = canvasRef.value
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
    cols.value = Math.ceil(canvas.width / cellSize)
    rows.value = Math.ceil(canvas.height / cellSize)
    gridData = Array.from({ length: rows.value }, () => Array(cols.value).fill(false))
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.fillStyle = cssColor
    drawGrid(ctx, canvas)
}

onMounted(() => {
    initCanvas()
    window.addEventListener('resize', initCanvas)
})

onBeforeUnmount(() => {
    window.removeEventListener('resize', initCanvas);
});
</script>

<template>
    <canvas
        ref="canvasRef"
        class="canvas"
        @mousemove="handleMouseMove"
    ></canvas>
</template>

<style scoped>
.canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}
</style>