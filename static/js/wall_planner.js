let obstacleCount = 0, animationId = null;
let wallData = null, rectangleColors = [];
let sectionTrajectories = [], currentSection=0, currentSectionStep=0;
let paintedCells = [];

// ----------------- Obstacles -----------------
function addObstacleInput() {
    const i = obstacleCount++;
    const div = document.createElement("div");
    div.classList.add("obstacle-box");
    div.id = `obsDiv${i}`;
    div.innerHTML = `
        <h4>Obstacle ${i+1}</h4>
        X:<input type="number" id="x${i}" value="5">
        Y:<input type="number" id="y${i}" value="5">
        Width:<input type="number" id="w${i}" value="5">
        Height:<input type="number" id="h${i}" value="5">
        <button onclick="removeObstacle(${i})">Remove</button>
    `;
    document.getElementById("obstacleInputs").appendChild(div);
}
function removeObstacle(i){ const div=document.getElementById(`obsDiv${i}`); if(div) div.remove(); }

// ----------------- Wall Submission -----------------
async function submitWall() {
    const width = parseInt(document.getElementById("wallWidth").value);
    const height = parseInt(document.getElementById("wallHeight").value);
    const obstacles = [];
    for(let i=0;i<obstacleCount;i++){
        const div=document.getElementById(`obsDiv${i}`);
        if(!div) continue;
        obstacles.push({
            x:parseInt(document.getElementById(`x${i}`).value),
            y:parseInt(document.getElementById(`y${i}`).value),
            width:parseInt(document.getElementById(`w${i}`).value),
            height:parseInt(document.getElementById(`h${i}`).value)
        });
    }
    await fetch("/add_wall",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({width,height,obstacles})
    });
    await drawWall();
}

// ----------------- Draw Wall -----------------
async function drawWall() {
    const canvas = document.getElementById("wallCanvas");
    const ctx = canvas.getContext("2d");
    const res = await fetch("/latest_wall");
    wallData = await res.json();
    sectionTrajectories = [];
    currentSection=0; currentSectionStep=0;
    paintedCells = [];

    ctx.clearRect(0,0,canvas.width,canvas.height);
    const scaleX = canvas.width / wallData.width;
    const scaleY = canvas.height / wallData.height;

    rectangleColors=[];
    wallData.rectangles.forEach(rect=>{
        const color=`hsla(${Math.random()*360},60%,90%,0.7)`;
        rectangleColors.push(color);
        ctx.fillStyle=color;
        ctx.fillRect(rect.x*scaleX,rect.y*scaleY,rect.width*scaleX,rect.height*scaleY);
    });

    ctx.fillStyle="#000";
    wallData.obstacles.forEach(ob=>{
        ctx.fillRect(ob.x*scaleX, ob.y*scaleY, ob.width*scaleX, ob.height*scaleY);
    });

    document.getElementById("paintingProgress").value=0;
    document.getElementById("paintingStatus").textContent="Not started";
    document.getElementById("trajectoryOutput").innerHTML="";
}

// ----------------- Trajectory -----------------
async function generateTrajectory(){
    if(!wallData) return;
    const wall_id = wallData.wall_id;
    const res = await fetch(`/calculate_trajectory/${wall_id}`);
    const data = await res.json();
    if(data.error){ document.getElementById("trajectoryOutput").textContent=data.error; return; }

    sectionTrajectories = data.section_paths.map(s=>s.path);
    drawSectionTrajectories();

    // Metrics
    const total=sectionTrajectories.flat().length;
    document.getElementById("totalCells").textContent = total;
    document.getElementById("totalTime").textContent = data.total_time_units.toFixed(2);

    // Show section-wise points
    const trajDiv = document.getElementById("trajectoryOutput");
    trajDiv.innerHTML = "";
    sectionTrajectories.forEach((path,i)=>{
        const secDiv = document.createElement("div");
        secDiv.classList.add("trajectory-section");
        secDiv.innerHTML = `<strong>Section ${i+1}:</strong> ${path.map(p=>`(${p[0]},${p[1]})`).join(" → ")}`;
        trajDiv.appendChild(secDiv);
    });
}

// ----------------- Draw section trajectories (arrows) -----------------
function drawSectionTrajectories(){
    if(!wallData) return;
    const canvas=document.getElementById("wallCanvas");
    const ctx=canvas.getContext("2d");
    const scaleX = canvas.width / wallData.width;
    const scaleY = canvas.height / wallData.height;

    wallData.rectangles.forEach((rect,i)=>{
        ctx.fillStyle = rectangleColors[i];
        ctx.fillRect(rect.x*scaleX, rect.y*scaleY, rect.width*scaleX, rect.height*scaleY);
    });

    ctx.fillStyle="#000";
    wallData.obstacles.forEach(ob=>{
        ctx.fillRect(ob.x*scaleX, ob.y*scaleY, ob.width*scaleX, ob.height*scaleY);
    });

    ctx.strokeStyle="blue"; ctx.lineWidth=1;
    sectionTrajectories.forEach(path=>{
        for(let i=0;i<path.length-1;i++){
            drawArrow(ctx,path[i][0]*scaleX+scaleX/2, path[i][1]*scaleY+scaleY/2,
                      path[i+1][0]*scaleX+scaleX/2, path[i+1][1]*scaleY+scaleY/2);
        }
    });
}

// ----------------- Animation -----------------
function animateSections(){
    if(currentSection>=sectionTrajectories.length){
        cancelAnimationFrame(animationId);
        animationId=null;
        document.getElementById("paintingStatus").textContent="Painting done!";
        return;
    }
    const speed=parseFloat(document.getElementById("speedSlider").value);
    currentSectionStep+=speed;
    const path = sectionTrajectories[currentSection];
    if(currentSectionStep>=path.length){
        currentSectionStep=path.length-1;
        drawSectionFrame(currentSection,currentSectionStep);
        paintedCells.push(...path);
        currentSection++; currentSectionStep=0;
    } else drawSectionFrame(currentSection,currentSectionStep);

    animationId=requestAnimationFrame(animateSections);
}

function drawSectionFrame(sectionIdx, stepIdx){
    if(!wallData) return;
    const canvas=document.getElementById("wallCanvas");
    const ctx=canvas.getContext("2d");
    const scaleX=canvas.width/wallData.width, scaleY=canvas.height/wallData.height;

    wallData.rectangles.forEach((rect,i)=>{
        ctx.fillStyle = rectangleColors[i];
        ctx.fillRect(rect.x*scaleX, rect.y*scaleY, rect.width*scaleX, rect.height*scaleY);
    });

    ctx.fillStyle="#000";
    wallData.obstacles.forEach(ob=>{
        ctx.fillRect(ob.x*scaleX, ob.y*scaleY, ob.width*scaleX, ob.height*scaleY);
    });

    ctx.fillStyle="rgba(0,0,139,0.8)";
    paintedCells.forEach(([x,y])=>ctx.fillRect(x*scaleX,y*scaleY,scaleX,scaleY));

    const path=sectionTrajectories[sectionIdx];
    ctx.fillStyle="rgba(0,0,139,0.8)";
    for(let i=0;i<=stepIdx && i<path.length;i++){
        const [x,y]=path[i];
        ctx.fillRect(x*scaleX,y*scaleY,scaleX,scaleY);
    }

    ctx.strokeStyle="blue"; ctx.lineWidth=1;
    for(let i=0;i<stepIdx && i<path.length-1;i++){
        const [x1,y1]=path[i], [x2,y2]=path[i+1];
        drawArrow(ctx,x1*scaleX+scaleX/2,y1*scaleY+scaleY/2,x2*scaleX+scaleX/2,y2*scaleY+scaleY/2);
    }

    const totalCells=sectionTrajectories.flat().length;
    const completed=paintedCells.length + Math.min(stepIdx,path.length);
    const progress=Math.min(completed/totalCells*100,100);
    document.getElementById("paintingProgress").value=progress;
    document.getElementById("paintingStatus").textContent=progress>=100?"Painting done!":`Painting in progress: ${progress.toFixed(1)}%`;
}

// ----------------- Arrow -----------------
function drawArrow(ctx,x1,y1,x2,y2){
    const headLen=5, dx=x2-x1, dy=y2-y1, angle=Math.atan2(dy,dx);
    ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x2,y2);
    ctx.lineTo(x2-headLen*Math.cos(angle-Math.PI/6),y2-headLen*Math.sin(angle-Math.PI/6));
    ctx.lineTo(x2-headLen*Math.cos(angle+Math.PI/6),y2-headLen*Math.sin(angle+Math.PI/6));
    ctx.lineTo(x2,y2); ctx.fillStyle="blue"; ctx.fill();
}

// ----------------- Controls -----------------
function startAnimation(){ if(animationId) cancelAnimationFrame(animationId); animationId=requestAnimationFrame(animateSections); }
function pauseAnimation(){ if(animationId) cancelAnimationFrame(animationId); animationId=null; }
function replayAnimation(){ if(animationId) cancelAnimationFrame(animationId); currentSection=0; currentSectionStep=0; paintedCells=[]; animationId=requestAnimationFrame(animateSections); }
