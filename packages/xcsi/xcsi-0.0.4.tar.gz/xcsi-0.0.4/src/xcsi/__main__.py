#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
from xcsi.csi import create_model, load, collect_outlines, find_rows
from xcsi.job import Job
from opensees.repl.ptkshell import OpenSeesREPL



def main():
    import sys

    file_name = None
    out_file = None
    operation = "View"
    strict_mode = None
    object_mode = "Model"
    interact = False
    show = set()
    objects = []

    ic = None
    i  = 0
    argi = iter(sys.argv[1:])
    for arg in argi:
        if arg == "-s":
            object_mode = "Section"
        elif arg == "-t":
            object_mode = next(argi)
            if object_mode not in ["Model", "Section", "Pattern", "Step"]:
                raise ValueError(f"Unknown object mode {object_mode}")

        elif arg == "-o":
            try:
                out_file = next(argi)
            except StopIteration:
                raise ValueError("Flag -o missing required argument <file>")

        elif arg == "-i":
            interact = True

        elif arg == "-m":
            try:
                strict_mode = next(argi)
            except StopIteration:
                raise ValueError("Flag -m missing required argument <mode>")
        
        elif arg == "--show":
            try:
                show.add(next(argi))
            except StopIteration:
                raise ValueError("Flag --show missing required argument <name>")

        elif arg[0] == "-":
            operation = {
                "p": "Print",
                "a": "Analyze",
                "c": "Convert",
                "x": "Execute",
                "v": "Visualize",
            }[arg[1].lower()]
            ic = i+1

        elif file_name is None:
            file_name = arg
        else:
            objects.append(arg.split("="))

        i += 1

    if file_name is None:
        raise ValueError("No file specified")
    

    with open(file_name, "r") as f:
        csi = load(f)


    if operation == "Convert":
        # Convert
        if "tcl" in sys.argv[1]:
            import xara 
            model = xara.Model(ndm=3, ndf=6, echo_file=sys.stdout)
            model = create_model(csi, model=model, verbose=False)

        else:
            model = create_model(csi, verbose=False)
            model.print("-json")
        sys.exit()

    
    if operation == "Print":
        job = Job(csi)
        if object_mode == "Pattern":
            for pattern in job.patterns():
                print(pattern)
        elif object_mode == "Step":
            for step in job.steps():
                print(step)
        elif len(objects) == 0:
            for table in csi:
                print(f"{table}: {len(csi[table])}")
        else:
            for key, value in objects:
                for table in csi:
                    filt = {key: value}
                    if (row:= find_rows(csi[table], **filt)):
                        print(table)
                        for r in row:
                            for k, v in r.items():
                                if k == key:
                                    continue
                                print(f"  {k:<10}      {v}")
                            print()
                            continue
        sys.exit()



    if operation == "Execute":
        job = Job(csi)

        asm = job.assemble()

        for step in job.steps():
            step.run(asm)
            break

        if interact:
        
            # Start an interactive console
            repl = OpenSeesREPL(asm.model._openseespy._interp)
            repl.repl()


    elif operation == "Visualize":

        # Visualize
        import veux
        model = create_model(csi, verbose=True)
        outlines = collect_outlines(csi, model.frame_tags)
        artist = veux.create_artist(model, canvas="gltf", vertical=3,
                    model_config={
                        "frame_outlines": outlines
                    }
        )
        # artist.draw_nodes()
        artist.draw_outlines()
        artist.draw_surfaces()


        if sys.argv[1] == "-Vo":
            artist.save(sys.argv[3])
        else:
            veux.serve(artist)

    elif sys.argv[1] == "-Vn":
        # Visualize
        from scipy.linalg import null_space
        model.constraints("Transformation")
        model.analysis("Static")
        K = model.getTangent().T
        v = null_space(K)[:,0] #, rcond=1e-8)
        print(v)


        u = {
            tag: [1000*v[dof-1] for dof in model.nodeDOFs(tag)]
            for tag in model.getNodeTags()
        }

        import veux
        veux.serve(veux.render(model, u, canvas="gltf", vertical=3))

    elif sys.argv[1] == "-Q":
        # Quiet conversion
        pass
    else:
        raise ValueError(f"Unknown operation {sys.argv[1]}")


if __name__ == "__main__":
    main()